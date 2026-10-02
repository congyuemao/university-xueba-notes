"""Run with: python -m unittest discover -s tests -v"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
from pick_fun_content import (DEFAULT_CATALOG, FunPicker, UsageHistory,
                              display_text, load_catalog, text_key)


class FunContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_catalog()

    def test_catalog_size_sources_and_layout(self):
        self.assertGreaterEqual(len(self.items), 900)
        sources = json.loads((DEFAULT_CATALOG.parent / 'sources.json').read_text(encoding='utf-8'))
        ids = {x['id'] for x in sources['sources']}
        for item in self.items:
            self.assertIn(item['source']['id'], ids)
            self.assertTrue(item['source']['url'].startswith('https://'))
            self.assertIn(item['layout']['lines'], (1, 2))
            self.assertEqual(item['layout']['characters'], len(display_text(item)))
            if item['kind'] == 'quote':
                self.assertTrue(item['author'])
                self.assertTrue(item['work'])

    def test_reproducible_and_varies_with_seed(self):
        def draw(seed):
            return [x['id'] for x in FunPicker(self.items, seed=seed).take(24)]
        self.assertEqual(draw(42), draw(42))
        self.assertNotEqual(draw(42), draw(43))

    def test_whole_catalog_without_replacement_and_exhaustion(self):
        picker = FunPicker(self.items, seed=17)
        all_items = picker.take(len(self.items))
        self.assertEqual(len({x['id'] for x in all_items}), len(self.items))
        self.assertEqual(len({text_key(x) for x in all_items}), len(self.items))
        with self.assertRaisesRegex(ValueError, '已用完'):
            picker.pick()

    def test_subject_and_kind_filters(self):
        items = FunPicker(self.items, seed=1, subjects=['统计学'], kinds=['subject_fact']).take(10)
        self.assertTrue(all('statistics' in x['subjects'] for x in items))
        self.assertTrue(all(x['kind'] == 'subject_fact' for x in items))
        with self.assertRaisesRegex(ValueError, '未知学科'):
            FunPicker(self.items, subjects=['不存在的课程'])
        broad = FunPicker(self.items, subjects=['统计学'], include_general=True)
        self.assertTrue(any(x['kind'] == 'joke' for x in broad.pool))
        self.assertTrue(all({'statistics', 'general'}.intersection(x['subjects']) for x in broad.pool))

    def test_categories_rotate(self):
        items = FunPicker(self.items, seed=42).take(16)
        for start in range(0, 16, 4):
            self.assertEqual({x['kind'] for x in items[start:start + 4]},
                             {'joke', 'quote', 'trivia', 'subject_fact'})

    def test_attribution_counts_toward_length(self):
        quote = next(x for x in self.items if x['kind'] == 'quote')
        with self.assertRaises(ValueError):
            FunPicker([quote], max_chars=len(quote['text'])).pick()

    def test_actual_layout_callback_overrides_reference_lines(self):
        records = [x for x in self.items if x['kind'] == 'joke'][:3]
        widths = {display_text(records[0]): 3, display_text(records[1]): 2,
                  display_text(records[2]): 1}
        picker = FunPicker(records, seed=1)
        self.assertEqual(picker.pick(widths.get)['id'], records[2]['id'])
        self.assertEqual(picker.pick(widths.get)['id'], records[1]['id'])
        with self.assertRaises(ValueError):
            picker.pick(widths.get)
        with self.assertRaises(ValueError):
            FunPicker([records[1]], max_lines=1).pick(widths.get)

    def test_history_across_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'used.json'
            with UsageHistory(path) as history:
                first = FunPicker(self.items, seed=42, history=history).take(20)
                history.commit(first)
            with UsageHistory(path) as history:
                second = FunPicker(self.items, seed=42, history=history).take(20)
                history.commit(second)
            self.assertFalse({x['id'] for x in first} & {x['id'] for x in second})
            self.assertEqual(len(json.loads(path.read_text(encoding='utf-8'))['used_ids']), 40)
            self.assertFalse(path.with_name('used.json.lock').exists())

    def test_history_matches_text_even_if_id_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'used.json'
            with UsageHistory(path) as history:
                history.commit([self.items[0]])
            changed = dict(self.items[0], id='new-id')
            with UsageHistory(path) as history:
                with self.assertRaises(ValueError):
                    FunPicker([changed], history=history).pick()

    def test_failed_generation_does_not_consume_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'used.json'
            with UsageHistory(path) as history:
                history.commit([self.items[0]])
            before = path.read_bytes()
            with self.assertRaises(RuntimeError):
                with UsageHistory(path) as history:
                    FunPicker(self.items, history=history).take(5)
                    raise RuntimeError('PDF generation failed')
            self.assertEqual(before, path.read_bytes())
            self.assertFalse(path.with_name('used.json.lock').exists())

    def test_shared_history_lock_and_invalid_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'used.json'
            with UsageHistory(path):
                with self.assertRaisesRegex(ValueError, '正在使用'):
                    with UsageHistory(path):
                        pass
                self.assertTrue(path.with_name('used.json.lock').exists())
            path.write_text('{"version": 999}', encoding='utf-8')
            with self.assertRaises(ValueError):
                with UsageHistory(path):
                    pass
            self.assertFalse(path.with_name('used.json.lock').exists())

    def test_cli_output_and_exhaustion(self):
        with tempfile.TemporaryDirectory() as directory:
            output, history = Path(directory) / 'selected.json', Path(directory) / 'used.json'
            cmd = [sys.executable, '-X', 'utf8', str(SKILL / 'scripts/pick_fun_content.py'),
                   '--types', 'joke', '--seed', '7', '--output', str(output), '--used-file', str(history)]
            subprocess.run(cmd + ['--count', '8'], check=True, capture_output=True)
            data = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(len(data['items']), 8)
            self.assertTrue(all(x['display_text'] == display_text(x) for x in data['items']))
            original_output, original_history = output.read_bytes(), history.read_bytes()
            failed = subprocess.run(cmd + ['--count', '9999'], capture_output=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(original_output, output.read_bytes())
            self.assertEqual(original_history, history.read_bytes())


if __name__ == '__main__':
    unittest.main()
