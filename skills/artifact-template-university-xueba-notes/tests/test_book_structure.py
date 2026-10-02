"""Structural regressions for contents, teaching and final glossary."""
import json
from pathlib import Path
import unittest

SKILL=Path(__file__).resolve().parents[1]

class BookStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content=json.loads((SKILL/'Resources/content/statistics-chapter.json').read_text(encoding='utf-8'))

    def test_legacy_front_and_test_vocabulary_are_absent(self):
        self.assertNotIn('terminology_extended',self.content)
        self.assertNotIn('answer_vocabulary',self.content)
        self.assertNotIn('glossary',self.content.get('frontmatter',{}))
        self.assertEqual([p['number'] for p in self.content['pages']],[1,2,3,4,5,6])
        for page in self.content['pages']:
            self.assertNotIn('english_terms',page.get('sidebar',{}))

    def test_outline_is_independent_and_anchored(self):
        outline={node['id']:node for node in self.content['outline']}
        self.assertTrue(any(node['level']==1 for node in outline.values()))
        self.assertTrue(any(node['level']==2 for node in outline.values()))
        anchors={oid for page in self.content['pages'] for oid in page['outline_ids']}
        for oid,node in outline.items():
            if node['kind']!='appendix':self.assertIn(oid,anchors)
        self.assertTrue(any(node['kind']=='appendix' for node in outline.values()))

    def test_core_concepts_have_first_use_teaching_fields(self):
        for concept in self.content['concepts']:
            self.assertTrue(concept['core'])
            for field in ('definition','plain_explanation','boundary','canonical_example'):
                self.assertTrue(concept[field].strip(),f"{concept['id']} missing {field}")

    def test_final_glossary_is_minimal_and_grouped(self):
        terms=set()
        for group in self.content['chapter_glossary']:
            self.assertTrue(group['chapter_id'])
            self.assertTrue(group['chapter_title'])
            for entry in group['entries']:
                self.assertEqual(set(entry),{'term_en','meaning_zh'})
                key=entry['term_en'].casefold()
                self.assertNotIn(key,terms);terms.add(key)
                self.assertTrue(entry['meaning_zh'].strip())
        self.assertGreaterEqual(len(terms),10)

    def test_templates_include_dedicated_contents_and_glossary_roles(self):
        manifest=json.loads((SKILL/'Resources/templates/template-manifest.json').read_text(encoding='utf-8'))
        for role in ('contents_odd','contents_even','glossary_odd','glossary_even'):
            self.assertIn(role,manifest['roles'])
            for edition in ('print','digital'):
                self.assertIn(role,manifest['editions'][edition])

if __name__=='__main__':unittest.main()
