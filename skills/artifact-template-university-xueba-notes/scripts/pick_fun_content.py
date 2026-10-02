#!/usr/bin/env python3
"""从随包语料中随机抽取短句；支持学科、类型、随机种子和跨次去重。"""
import argparse
from collections import Counter
from contextlib import AbstractContextManager
import json
import os
from pathlib import Path
import random
import re
import tempfile
import unicodedata

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / 'Resources/fun-content/items.jsonl'
KINDS = ('joke', 'trivia', 'subject_fact', 'quote')
SUBJECTS = {
    'general': '通用', 'mathematics': '数学', 'statistics': '统计学',
    'physics': '物理', 'chemistry': '化学', 'biology': '生物',
    'astronomy': '天文', 'earth_science': '地球科学',
    'computer_science': '计算机', 'literature': '文学', 'language': '语言',
}
ALIASES = {v: k for k, v in SUBJECTS.items()}
ALIASES.update({'统计': 'statistics', '概率': 'statistics', '微积分': 'mathematics',
                '高数': 'mathematics', '地理': 'earth_science', '英语': 'language',
                '语文': 'literature', '编程': 'computer_science'})


def display_text(item):
    """署名参加长度计算；篇名和来源放在JSON中。"""
    return item['text'] + ('——' + item['author'] if item.get('author') else '')


def text_key(item):
    return re.sub(r'\W', '', unicodedata.normalize('NFKC', display_text(item))).casefold()


def subject_key(value):
    value = ALIASES.get(value, value)
    if value not in SUBJECTS:
        raise ValueError(f'未知学科：{value}；可选：' + '、'.join(SUBJECTS.values()))
    return value


def load_catalog(path=DEFAULT_CATALOG):
    items = []
    ids, texts = set(), set()
    for number, line in enumerate(Path(path).read_text(encoding='utf-8-sig').splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        if (not isinstance(item.get('id'), str) or not item['id']
                or item.get('kind') not in KINDS
                or not isinstance(item.get('text'), str) or not item['text'].strip()
                or '\n' in item['text'] or '\r' in item['text']
                or not isinstance(item.get('subjects'), list) or not item['subjects']
                or any(s not in SUBJECTS for s in item['subjects'])):
            raise ValueError(f'语料第{number}行字段不完整或类型错误')
        key = text_key(item)
        if item['id'] in ids or key in texts:
            raise ValueError(f'语料第{number}行重复：{item["id"]}')
        ids.add(item['id'])
        texts.add(key)
        items.append(item)
    if not items:
        raise ValueError('语料库为空')
    return sorted(items, key=lambda item: item['id'])


def write_json(path, data):
    """在同一目录完成写入后替换，避免留下半截JSON。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='\n',
                                         dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class UsageHistory(AbstractContextManager):
    """同一历史文件每次只供一个生成任务使用；成功后由调用方提交。"""
    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.ids, self.texts = set(), set()
        self.lock = None

    def __enter__(self):
        if self.path is None:
            return self
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock = self.path.with_name(self.path.name + '.lock')
        try:
            with lock.open('x', encoding='utf-8') as stream:
                stream.write(str(os.getpid()))
        except FileExistsError:
            raise ValueError(f'历史文件正在使用：{self.path}。若上次任务异常中断，确认进程结束后删除 {lock.name}。') from None
        self.lock = lock
        try:
            if self.path.exists():
                data = json.loads(self.path.read_text(encoding='utf-8'))
                if (data.get('version') != 1
                        or not isinstance(data.get('used_ids'), list)
                        or not isinstance(data.get('used_texts'), list)
                        or not all(isinstance(s, str) for s in data['used_ids'] + data['used_texts'])):
                    raise ValueError('无法读取历史文件：需要version、used_ids和used_texts字段')
                self.ids, self.texts = set(data['used_ids']), set(data['used_texts'])
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    def commit(self, items):
        if self.path is None:
            return
        write_json(self.path, {'version': 1,
                              'used_ids': sorted(self.ids | {x['id'] for x in items}),
                              'used_texts': sorted(self.texts | {text_key(x) for x in items})})

    def __exit__(self, *exc):
        if self.lock is not None:
            self.lock.unlink(missing_ok=True)
            self.lock = None
        return False


class FunPicker:
    """按类型轮换，类型内随机抽样；优先一行，不放回、不自动重置历史。"""
    def __init__(self, items, *, seed=None, subjects=None, kinds=None,
                 include_general=False, max_chars=70, max_lines=2, history=None):
        if max_chars < 1 or max_lines not in (1, 2):
            raise ValueError('max_chars必须为正数；max_lines只能为1或2')
        wanted = {subject_key(x) for x in subjects or []}
        if wanted and include_general:
            wanted.add('general')
        chosen_kinds = set(kinds or KINDS)
        if not chosen_kinds <= set(KINDS):
            raise ValueError('未知类型：' + ', '.join(sorted(chosen_kinds - set(KINDS))))
        used_ids, used_texts = (history.ids, history.texts) if history else (set(), set())
        self.pool = [x for x in items
                     if x['kind'] in chosen_kinds
                     and (not wanted or wanted.intersection(x['subjects']))
                     and x['id'] not in used_ids and text_key(x) not in used_texts
                     and len(display_text(x)) <= max_chars]
        self.rng = random.Random(seed)
        self.max_lines = max_lines
        self.selected = []
        self.counts = Counter()

    def pick(self, line_counter=None):
        # PDF调用方传入当前版式的真实折行函数；独立CLI用随包排版测量值。
        eligible = []
        for item in self.pool:
            lines = (line_counter(display_text(item)) if line_counter
                     else item.get('layout', {}).get('lines'))
            if not isinstance(lines, int):
                raise ValueError('语料缺少layout.lines；请提供字体进行实际测量')
            if 1 <= lines <= self.max_lines:
                eligible.append((item, lines))
        if not eligible:
            raise ValueError('符合学科、长度和去重条件的语料已用完；可扩大筛选范围或换用新书的历史文件。')
        # 优先轮到使用次数最少的类型，再优先该类型的一行内容。
        kinds = sorted({item['kind'] for item, _ in eligible})
        least = min(self.counts[kind] for kind in kinds)
        kind = self.rng.choice([kind for kind in kinds if self.counts[kind] == least])
        group = [(item, lines) for item, lines in eligible if item['kind'] == kind]
        shortest = min(lines for _, lines in group)
        item = self.rng.choice([item for item, lines in group if lines == shortest])
        self.pool = [x for x in self.pool if x['id'] != item['id'] and text_key(x) != text_key(item)]
        self.selected.append(item)
        self.counts[kind] += 1
        return item

    def take(self, count, line_counter=None):
        if count < 0:
            raise ValueError('抽取数量不能为负数')
        return [self.pick(line_counter) for _ in range(count)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=DEFAULT_CATALOG)
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--subject', action='append', help='学科中文名或英文键；可重复使用')
    parser.add_argument('--include-general', action='store_true', help='按学科筛选时也纳入通用笑话和名句')
    parser.add_argument('--types', nargs='+', choices=KINDS)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--max-chars', type=int, default=70, help='含名言署名的字符数上限')
    parser.add_argument('--max-lines', type=int, choices=(1, 2), default=2)
    parser.add_argument('--used-file', type=Path, help='同一本书各章节共享的已用记录')
    parser.add_argument('--fonts', type=Path, help='可选：用项目字体重新测量每条的行数')
    parser.add_argument('--width-mm', type=float, default=172, help='文字可用宽度，默认打印版页脚172mm')
    parser.add_argument('--output', type=Path, help='保存完整结构化结果；不指定时输出JSON到终端')
    args = parser.parse_args()
    try:
        if args.output and args.used_file and args.output.resolve() == args.used_file.resolve():
            raise ValueError('输出文件和历史文件须使用不同路径')
        if any(path and path.resolve() == args.catalog.resolve() for path in (args.output, args.used_file)):
            raise ValueError('输出或历史文件不能覆盖语料库')
        if args.width_mm <= 0:
            raise ValueError('文字宽度必须大于0')
        counter = None
        if args.fonts:
            from pdf_template_layout import register_fonts, wrap
            register_fonts(args.fonts)
            def counter(text):
                try:
                    return len(wrap(text, args.width_mm, 'Hand', 10))
                except ValueError:
                    return 3
        elif args.width_mm != 172:
            raise ValueError('改变文字宽度时请同时提供--fonts')
        with UsageHistory(args.used_file) as history:
            picker = FunPicker(load_catalog(args.catalog), seed=args.seed, subjects=args.subject,
                               kinds=args.types, include_general=args.include_general,
                               max_chars=args.max_chars, max_lines=args.max_lines, history=history)
            items = picker.take(args.count, counter)
            result = {'version': 1, 'seed': args.seed, 'count': len(items),
                      'items': [dict(item, display_text=display_text(item)) for item in items]}
            if args.output:
                write_json(args.output, result)
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            history.commit(items)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
