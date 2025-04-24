import unittest
import asyncio
from datetime import datetime
import os
import time
import streamlit as st
from unittest.mock import MagicMock, patch
from llm_processor import LLMProcessor
from chronology_generator import ChronologyGenerator
from utils import process_pdf
import generate_test_docs

class TestIntegration(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment and generate test documents"""
        # Generate test documents
        generate_test_docs.generate_simple_timeline()
        generate_test_docs.generate_complex_multiparty()
        generate_test_docs.generate_large_document()
        generate_test_docs.generate_mixed_format_dates()
        generate_test_docs.generate_nested_events()
        
        # Initialize components
        cls.llm_processor = LLMProcessor()
        cls.chronology_generator = ChronologyGenerator()
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        
    async def test_simple_timeline_processing(self):
        """Test processing of a simple timeline case"""
        # Process simple timeline document
        file_path = os.path.join(self.test_data_dir, 'simple_timeline.pdf')
        with open(file_path, 'rb') as f:
            text_content = process_pdf(f)
        
        # Extract events
        events = await self.llm_processor.extract_events(text_content, "simple_timeline.pdf")
        
        # Generate chronology
        chronology = await self.llm_processor.create_chronology(events, "Test case")
        
        # Assertions
        self.assertTrue(len(events) >= 6)  # Should have at least 6 events
        self.assertTrue(all('date' in event for event in events))
        self.assertTrue(all('description' in event for event in events))
        
        # Verify chronological order
        dates = [datetime.strptime(event['date'], '%Y-%m-%d') for event in chronology['events']]
        self.assertEqual(dates, sorted(dates))

    async def test_complex_multiparty_processing(self):
        """Test processing of a complex multi-party case"""
        # Process complex multiparty document
        file_path = os.path.join(self.test_data_dir, 'complex_multiparty.pdf')
        with open(file_path, 'rb') as f:
            text_content = process_pdf(f)
        
        # Extract events
        events = await self.llm_processor.extract_events(text_content, "complex_multiparty.pdf")
        
        # Generate chronology
        chronology = await self.llm_processor.create_chronology(events, "Test case")
        
        # Assertions
        self.assertTrue(len(events) >= 9)  # Should have at least 9 events
        
        # Verify all companies are mentioned
        all_text = ' '.join(event['description'] for event in events)
        companies = ['Company A', 'Company B', 'Company C', 'Company D']
        for company in companies:
            self.assertIn(company, all_text)
            
        # Verify chronological order
        dates = [datetime.strptime(event['date'], '%Y-%m-%d') for event in chronology['events']]
        self.assertEqual(dates, sorted(dates))

    async def test_large_document_performance(self):
        """Test performance with a large document"""
        # Process large document
        file_path = os.path.join(self.test_data_dir, 'large_document.pdf')
        
        # Measure PDF processing time
        start_time = time.time()
        with open(file_path, 'rb') as f:
            text_content = process_pdf(f)
        pdf_processing_time = time.time() - start_time
        
        # Measure event extraction time
        start_time = time.time()
        events = await self.llm_processor.extract_events(text_content, "large_document.pdf")
        event_extraction_time = time.time() - start_time
        
        # Measure chronology generation time
        start_time = time.time()
        chronology = await self.llm_processor.create_chronology(events, "Test case")
        chronology_generation_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(pdf_processing_time, 5.0)  # PDF processing should take less than 5 seconds
        self.assertLess(event_extraction_time, 30.0)  # Event extraction should take less than 30 seconds
        self.assertLess(chronology_generation_time, 10.0)  # Chronology generation should take less than 10 seconds
        
        # Verify number of events
        self.assertEqual(len(events), 100)  # Should have exactly 100 events

    async def test_mixed_date_format_handling(self):
        """Test handling of various date formats"""
        # Process document with mixed date formats
        file_path = os.path.join(self.test_data_dir, 'mixed_date_formats.pdf')
        with open(file_path, 'rb') as f:
            text_content = process_pdf(f)
        
        # Extract events
        events = await self.llm_processor.extract_events(text_content, "mixed_date_formats.pdf")
        
        # Generate chronology
        chronology = await self.llm_processor.create_chronology(events, "Test case")
        
        # Verify all dates are standardized to YYYY-MM-DD format
        date_format = '%Y-%m-%d'
        for event in chronology['events']:
            try:
                datetime.strptime(event['date'], date_format)
            except ValueError:
                self.fail(f"Date {event['date']} is not in YYYY-MM-DD format")

    async def test_nested_events_handling(self):
        """Test handling of nested and related events"""
        # Process document with nested events
        file_path = os.path.join(self.test_data_dir, 'nested_events.pdf')
        with open(file_path, 'rb') as f:
            text_content = process_pdf(f)
        
        # Extract events
        events = await self.llm_processor.extract_events(text_content, "nested_events.pdf")
        
        # Generate chronology
        chronology = await self.llm_processor.create_chronology(events, "Test case")
        
        # Verify all events are captured
        self.assertTrue(len(events) >= 10)  # Should have at least 10 events
        
        # Verify parent-child relationships are maintained
        main_events = [event for event in events if 'Main contract' in event['description']]
        self.assertTrue(len(main_events) > 0)
        
        # Verify chronological order
        dates = [datetime.strptime(event['date'], '%Y-%m-%d') for event in chronology['events']]
        self.assertEqual(dates, sorted(dates))

    async def test_error_handling(self):
        """Test error handling for various edge cases"""
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            with open('non_existent.pdf', 'rb') as f:
                process_pdf(f)
        
        # Test with empty text
        events = await self.llm_processor.extract_events("", "empty.pdf")
        self.assertEqual(len(events), 0)
        
        # Test with text containing no dates
        events = await self.llm_processor.extract_events("This text contains no dates or events.", "no_dates.pdf")
        self.assertEqual(len(events), 0)
        
        # Test with invalid date formats
        events = await self.llm_processor.extract_events("Invalid date: 13/13/2024: Something happened", "invalid_dates.pdf")
        chronology = await self.llm_processor.create_chronology(events, "Test case")
        self.assertTrue('errors' in chronology or len(chronology['events']) == 0)

if __name__ == '__main__':
    asyncio.run(unittest.main()) 