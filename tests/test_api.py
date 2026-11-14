from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from filechat import app

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = MagicMock()
        app.config.update(TESTING=True, DATA_DIR=self.root, STORE_FACTORY=lambda name: self.store,
                          ANSWER_FACTORY=lambda question, context: 'Answer from context')
        self.client = app.test_client()

    def tearDown(self):
        self.temp.cleanup()
        app.config.pop('STORE_FACTORY', None)
        app.config.pop('ANSWER_FACTORY', None)

    def test_bad_json_and_missing_fields(self):
        for body in [None, [], {}, {'collection_name': 'demo'}, {'collection_name': 9, 'query': 'x'}]:
            response = self.client.post('/query', json=body)
            self.assertEqual(response.status_code, 400)
        self.store.assert_not_called()

    def test_collection_is_not_a_sql_identifier(self):
        response = self.client.post('/query', json={'collection_name': 'x; DROP TABLE x', 'query': 'x'})
        self.assertEqual(response.status_code, 400)
        self.store.similarity_search_with_score.assert_not_called()

    def test_paths_cannot_escape_root_or_read_configuration(self):
        for value in ['../secret.txt', '/etc/passwd', '.env', 'missing.txt']:
            response = self.client.post('/add', json={'collection_name': 'demo', 'document_path': value})
            self.assertEqual(response.status_code, 400)
        self.store.add_texts.assert_not_called()

    def test_symlink_escape_is_rejected(self):
        with TemporaryDirectory() as outside:
            source = Path(outside) / 'secret.txt'
            source.write_text('secret')
            (self.root / 'link.txt').symlink_to(source)
            response = self.client.post('/add', json={'collection_name': 'demo', 'document_path': 'link.txt'})
            self.assertEqual(response.status_code, 400)

    def test_indexing_preserves_source_metadata(self):
        (self.root / 'sample.txt').write_text('Example document. ' * 200)
        response = self.client.post('/add', json={'collection_name': 'demo', 'document_path': 'sample.txt'})
        self.assertEqual(response.status_code, 200)
        args, kwargs = self.store.add_texts.call_args
        self.assertGreater(len(args[0]), 1)
        self.assertTrue(all(m == {'source': 'sample.txt'} for m in kwargs['metadatas']))

    def test_query_returns_answer_and_sources(self):
        self.store.similarity_search_with_score.return_value = [(SimpleNamespace(page_content='Facts', metadata={'source': 'sample.txt'}), 0.1)]
        response = self.client.post('/query', json={'collection_name': 'demo', 'query': 'What?'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'answer': 'Answer from context', 'sources': ['sample.txt']})

    def test_empty_collection_does_not_call_model(self):
        self.store.similarity_search_with_score.return_value = []
        with patch('filechat.answer') as answer:
            response = self.client.post('/query', json={'collection_name': 'demo', 'query': 'What?'})
            self.assertEqual(response.status_code, 200)
            answer.assert_not_called()

    def test_sql_example_parameterizes_collection(self):
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-only'}), patch('filechat.embeddings') as embeddings:
            embeddings.return_value.embed_query.return_value = [0.1, 0.2]
            response = self.client.post('/sql', json={'collection_name': 'demo', 'query': 'What?'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('%(collection_name)s', response.json['sql_query'])
            self.assertEqual(response.json['parameters']['collection_name'], 'demo')

if __name__ == '__main__':
    unittest.main()
