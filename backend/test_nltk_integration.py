#!/usr/bin/env python3
"""
Test NLTK Integration for DocumentFiller v3.0
Verifies that all NLTK components work correctly in backend
"""

import sys
import os

# Test 1: NLTK data availability
def test_nltk_data():
    """Test that all required NLTK data is available"""
    print("=" * 60)
    print("TEST 1: NLTK Data Availability")
    print("=" * 60)

    try:
        import nltk

        datasets = {
            'punkt': 'tokenizers/punkt',
            'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
            'stopwords': 'corpora/stopwords'
        }

        all_found = True
        for name, path in datasets.items():
            try:
                nltk.data.find(path)
                print(f"✅ {name}: Found")
            except LookupError:
                print(f"❌ {name}: NOT FOUND")
                all_found = False

        if all_found:
            print("\n✅ All NLTK data is available")
            return True
        else:
            print("\n❌ Some NLTK data is missing")
            return False

    except ImportError as e:
        print(f"❌ NLTK not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Test 2: DocumentReviewer import and basic functionality
def test_document_reviewer():
    """Test DocumentReviewer import and basic functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: DocumentReviewer Functionality")
    print("=" * 60)

    try:
        from document_reviewer import TechnicalDocumentReviewer

        print("✅ DocumentReviewer imported successfully")

        # Create instance with minimal config
        config = {
            'base_url': 'http://localhost:11434',
            'api_key': 'test_key',
            'review_model': 'llama3.1:latest'
        }

        reviewer = TechnicalDocumentReviewer(config)
        print("✅ DocumentReviewer instance created")

        # Test tense analysis
        test_content = """
        This is a test document. The system processes requests efficiently.
        It was designed to handle complex workflows. The architecture
        supports scalability and maintainability. It will be enhanced further.
        """

        tense_analysis = reviewer.analyze_tense_consistency(test_content)
        print(f"\n  Tense Analysis:")
        print(f"  - Dominant tense: {tense_analysis.dominant_tense}")
        print(f"  - Consistency score: {tense_analysis.consistency_score:.2f}")
        print(f"  - Past count: {tense_analysis.past_count}")
        print(f"  - Present count: {tense_analysis.present_count}")
        print(f"  - Future count: {tense_analysis.future_count}")
        print(f"  - Inconsistent sentences: {len(tense_analysis.inconsistent_sentences)}")

        # Test readability metrics
        try:
            readability = reviewer.calculate_readability_metrics(test_content)
            print(f"\n  Readability Metrics:")
            print(f"  - Flesch score: {readability.flesch_score:.2f}")
            print(f"  - Grade level: {readability.grade_level:.2f}")
            print(f"  - Avg sentence length: {readability.avg_sentence_length:.2f}")
            print(f"  - Complex word ratio: {readability.complex_word_ratio:.2f}")
            print(f"  - Passive voice ratio: {readability.passive_voice_ratio:.2f}")
            print("✅ Readability metrics calculated")
        except Exception as e:
            print(f"⚠️  Readability metrics failed (textstat may be missing): {e}")

        # Test coherence analysis
        coherence = reviewer.analyze_coherence(test_content)
        print(f"\n  Coherence Analysis:")
        print(f"  - Transition score: {coherence.transition_score:.2f}")
        print(f"  - Topic consistency: {coherence.topic_consistency:.2f}")
        print(f"  - Logical flow: {coherence.logical_flow:.2f}")
        print("✅ Coherence analysis completed")

        # Test comprehensive report
        report = reviewer.generate_comprehensive_report(test_content, "Test Section")
        print(f"\n  Comprehensive Report:")
        print(f"  - Overall score: {report['overall_score']:.2f}")
        print(f"  - Word count: {report['word_count']}")
        print(f"  - Recommendation: {report['recommendation'][:100]}...")
        print("✅ Comprehensive report generated")

        print("\n✅ All DocumentReviewer tests passed")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ DocumentReviewer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test 3: ContentProcessor import and basic functionality
def test_content_processor():
    """Test ContentProcessor import and basic functionality"""
    print("\n" + "=" * 60)
    print("TEST 3: ContentProcessor Functionality")
    print("=" * 60)

    try:
        from content_processor import IntelligentContentProcessor

        print("✅ ContentProcessor imported successfully")

        # Create instance with minimal config
        config = {
            'rag_threshold': 10000,
            'max_prompt_tokens': 8000,
            'chunk_size': 1000,
            'chunk_overlap': 100,
            'document_store_path': '/tmp/test_document_store.db'
        }

        processor = IntelligentContentProcessor(config)
        print("✅ ContentProcessor instance created")

        # Test content metrics analysis
        test_content = """
        This is a test technical document. The system architecture implements
        a robust processing framework. Configuration parameters control the
        operational behavior. The implementation follows best practices for
        scalability and maintainability. Interface specifications define the
        protocol for inter-component communication.
        """ * 10  # Make it longer

        metrics = processor.analyze_content_metrics(test_content)
        print(f"\n  Content Metrics:")
        print(f"  - Character count: {metrics.char_count}")
        print(f"  - Token count: {metrics.token_count}")
        print(f"  - Complexity score: {metrics.complexity_score:.2f}")
        print(f"  - Technical density: {metrics.technical_density:.2f}")
        print(f"  - Section count: {metrics.section_count}")
        print("✅ Content metrics calculated")

        # Test processing strategy determination
        strategy = processor.determine_processing_strategy(test_content)
        print(f"\n  Processing Strategy:")
        print(f"  - Method: {strategy.method}")
        print(f"  - Reason: {strategy.reason}")
        print(f"  - Token estimate: {strategy.token_estimate}")
        print(f"  - Confidence: {strategy.confidence:.2f}")
        print("✅ Processing strategy determined")

        # Test chunking
        chunks = processor.chunk_content(test_content, "/test/document.docx")
        print(f"\n  Content Chunking:")
        print(f"  - Chunks created: {len(chunks)}")
        if chunks:
            print(f"  - First chunk size: {chunks[0].char_count} chars")
            print(f"  - First chunk tokens: {chunks[0].token_count}")
        print("✅ Content chunking completed")

        # Test stats
        stats = processor.get_processing_stats()
        print(f"\n  Processing Stats:")
        print(f"  - Total documents: {stats.get('total_documents', 0)}")
        print(f"  - Total chunks: {stats.get('total_chunks', 0)}")
        print("✅ Processing stats retrieved")

        print("\n✅ All ContentProcessor tests passed")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ ContentProcessor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test 4: Backend API imports
def test_backend_imports():
    """Test that backend can import the modules"""
    print("\n" + "=" * 60)
    print("TEST 4: Backend API Imports")
    print("=" * 60)

    try:
        # Test imports from backend
        from app_enhanced import app
        print("✅ app_enhanced.py imports successfully")

        # Verify routes exist
        routes = [route.path for route in app.routes]
        critical_routes = ['/api/review', '/api/generate', '/api/auth/login']

        for route in critical_routes:
            if any(r.startswith(route) for r in routes):
                print(f"✅ Route {route} exists")
            else:
                print(f"⚠️  Route {route} not found")

        print("\n✅ Backend imports test passed")
        return True

    except ImportError as e:
        print(f"❌ Backend import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Backend imports test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Main test runner
def run_all_tests():
    """Run all NLTK integration tests"""
    print("\n" + "=" * 60)
    print("NLTK INTEGRATION TEST SUITE - DocumentFiller v3.0")
    print("=" * 60 + "\n")

    results = {
        'NLTK Data': test_nltk_data(),
        'DocumentReviewer': test_document_reviewer(),
        'ContentProcessor': test_content_processor(),
        'Backend Imports': test_backend_imports()
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())

    print("\n" + "=" * 60)
    print(f"OVERALL: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("✅ ALL TESTS PASSED - NLTK integration is working correctly!")
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")

    print("=" * 60 + "\n")

    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
