import pytest
from unittest.mock import patch, MagicMock
from agent.tools import (
    web_search_tool, arxiv_search_tool, wikipedia_tool,
    calculator_tool, python_repl_tool
)


class TestWebSearchTool:
    """Test web search tool"""

    @patch('agent.tools.requests.post')
    def test_web_search_success(self, mock_post):
        """Test successful web search"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'organic': [
                {'title': 'Result 1', 'link': 'http://example.com', 'snippet': 'Example snippet'}
            ]
        }
        mock_post.return_value = mock_response

        result = web_search_tool('python programming')

        assert isinstance(result, dict)
        assert result['success'] is True
        assert 'Result 1' in result['content']
        assert result['source_url'] == 'http://example.com'

    @patch('agent.tools.requests.post')
    def test_web_search_empty_results(self, mock_post):
        """Test web search with no results"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'organic': []}
        mock_post.return_value = mock_response

        result = web_search_tool('nonexistent query xyz')

        assert isinstance(result, dict)
        assert result['success'] is True
        assert 'No search results' in result['content']

    def test_web_search_missing_api_key(self):
        """Test web search when no Serper API key is configured"""
        with patch('agent.tools.settings') as mock_settings:
            mock_settings.SERPER_API_KEY = ''
            result = web_search_tool('python programming')

        assert result['success'] is False
        assert 'not configured' in result['content']


class TestArxivSearchTool:
    """Test arXiv search tool"""

    @patch('agent.tools.arxiv.Client')
    def test_arxiv_search_success(self, mock_client_cls):
        """Test successful arXiv search"""
        mock_author = MagicMock()
        mock_author.name = 'Jane Doe'

        mock_paper = MagicMock()
        mock_paper.title = 'Test Paper'
        mock_paper.entry_id = 'http://arxiv.org/abs/2301.00001'
        mock_paper.summary = 'Test summary'
        mock_paper.authors = [mock_author]

        mock_client = MagicMock()
        mock_client.results.return_value = [mock_paper]
        mock_client_cls.return_value = mock_client

        result = arxiv_search_tool('machine learning')

        assert isinstance(result, dict)
        assert result['success'] is True
        assert 'Test Paper' in result['content']
        assert result['source_url'] == 'http://arxiv.org/abs/2301.00001'

    @patch('agent.tools.arxiv.Client')
    def test_arxiv_search_no_results(self, mock_client_cls):
        """Test arXiv search with no matching papers"""
        mock_client = MagicMock()
        mock_client.results.return_value = []
        mock_client_cls.return_value = mock_client

        result = arxiv_search_tool('a query with no results')

        assert result['success'] is True
        assert 'No arXiv papers found' in result['content']


class TestWikipediaTool:
    """Test Wikipedia tool"""

    @patch('agent.tools.requests.get')
    @patch('agent.tools.wikipediaapi.Wikipedia')
    def test_wikipedia_search_success(self, mock_wikipedia_cls, mock_requests_get):
        """Test successful Wikipedia search"""
        mock_search_resp = MagicMock()
        mock_search_resp.json.return_value = {
            'query': {'search': [{'title': 'Python (programming language)'}]}
        }
        mock_requests_get.return_value = mock_search_resp

        mock_page = MagicMock()
        mock_page.exists.return_value = True
        mock_page.title = 'Python (programming language)'
        mock_page.summary = 'Python is a programming language.'
        mock_page.fullurl = 'https://en.wikipedia.org/wiki/Python'

        mock_wiki = MagicMock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia_cls.return_value = mock_wiki

        result = wikipedia_tool('Python programming')

        assert result['success'] is True
        assert 'Python' in result['content']
        assert result['source_url'] == 'https://en.wikipedia.org/wiki/Python'

    @patch('agent.tools.requests.get')
    @patch('agent.tools.wikipediaapi.Wikipedia')
    def test_wikipedia_search_not_found(self, mock_wikipedia_cls, mock_requests_get):
        """Test Wikipedia search not found"""
        mock_search_resp = MagicMock()
        mock_search_resp.json.return_value = {'query': {'search': []}}
        mock_requests_get.return_value = mock_search_resp

        mock_page = MagicMock()
        mock_page.exists.return_value = False

        mock_wiki = MagicMock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia_cls.return_value = mock_wiki

        result = wikipedia_tool('nonexistent xyz page')

        assert result['success'] is False
        assert 'No Wikipedia page found' in result['content']


class TestCalculatorTool:
    """Test calculator tool"""

    def test_calculator_addition(self):
        """Test calculator addition"""
        result = calculator_tool('5 + 3')
        assert result['content'] == '8'

    def test_calculator_subtraction(self):
        """Test calculator subtraction"""
        result = calculator_tool('10 - 3')
        assert result['content'] == '7'

    def test_calculator_multiplication(self):
        """Test calculator multiplication"""
        result = calculator_tool('4 * 5')
        assert result['content'] == '20'

    def test_calculator_division(self):
        """Test calculator division"""
        result = calculator_tool('10 / 2')
        assert result['content'] == '5.0'

    def test_calculator_invalid_expression(self):
        """Test calculator with invalid expression"""
        result = calculator_tool('invalid expression @@')
        assert result['success'] is False
        assert 'error' in result['content'].lower()


class TestPythonReplTool:
    """Test Python REPL tool"""

    def test_python_repl_simple(self):
        """Test Python REPL with simple code"""
        result = python_repl_tool('x = 5 + 3\nprint(x)')
        assert result['success'] is True
        assert '8' in result['content']

    def test_python_repl_list(self):
        """Test Python REPL with list operations"""
        result = python_repl_tool('print([1, 2, 3, 4, 5])')
        assert result['success'] is True
        assert '[1, 2, 3, 4, 5]' in result['content']

    def test_python_repl_invalid_syntax(self):
        """Test Python REPL with syntax error"""
        result = python_repl_tool('invalid python code @@')
        assert result['success'] is False
        assert 'failed' in result['content'].lower()

    def test_python_repl_import_restrictions(self):
        """Test that dangerous imports are restricted"""
        result = python_repl_tool('import os; os.system("rm -rf /")')
        assert result['success'] is False
        assert 'failed' in result['content'].lower()
