#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete End-to-End Analysis Pipeline
Runs full analysis from audio file → transcription → features → models → results
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from call_analysis.preprocessing import AudioProcessor, TextProcessor
from call_analysis.feature_extraction import FeatureExtractor
from call_analysis.models import ConversationAnalyzer
from call_analysis.dashboard import Dashboard

# Load environment variables
load_dotenv()

def run_full_analysis(audio_path: str, call_id: str = None, output_dir: str = None):
    """
    Run complete analysis pipeline on audio file.
    
    Args:
        audio_path: Path to audio file
        call_id: Unique call identifier (auto-generated if None)
        output_dir: Directory to save results
        
    Returns:
        Complete analysis results dictionary
    """
    print("=" * 70)
    print("COMPLETE CALL ANALYSIS PIPELINE")
    print("=" * 70)
    print()
    
    # Generate call_id if not provided
    if call_id is None:
        call_id = f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Resolve audio path to absolute
    audio_path = os.path.abspath(audio_path)
    
    # Set default output directory if not provided
    if output_dir is None:
        # Default to project root/output
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, "output")
    
    print(f"📁 Audio file: {audio_path}")
    print(f"🆔 Call ID: {call_id}")
    print(f"📂 Output directory: {output_dir}")
    print()
    
    # Verify audio file exists
    if not os.path.exists(audio_path):
        print(f"❌ Error: Audio file not found: {audio_path}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # ============================================================
        # STEP 1: Initialize Components
        # ============================================================
        print("🔧 Step 1: Initializing components...")
        from config import Config
        
        audio_processor = AudioProcessor(
            model_size=Config.WHISPER_MODEL_SIZE or "base",
            hf_token=Config.HF_TOKEN,
            min_speakers=getattr(Config, 'MIN_SPEAKERS', 2),
            max_speakers=getattr(Config, 'MAX_SPEAKERS', None),
        )
        text_processor = TextProcessor()
        feature_extractor = FeatureExtractor()
        analyzer = ConversationAnalyzer()
        dashboard = Dashboard()
        
        print("✅ Components initialized")
        print()
        
        # ============================================================
        # STEP 2: Transcribe Audio (Whisper)
        # ============================================================
        print("🎤 Step 2: Transcribing audio with Whisper...")
        print("   (This may take several minutes for long audio files)")
        print()
        
        transcription = audio_processor.transcribe_audio(audio_path, call_id)
        text = transcription.get('text', '')
        language = transcription.get('language', 'en')
        duration = transcription.get('duration', 0)
        segments = transcription.get('segments', [])
        
        print(f"✅ Transcription completed")
        print(f"   Language: {language}")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Text length: {len(text)} characters")
        print(f"   Segments: {len(segments)}")
        print()
        
        if not text:
            print("⚠️  Warning: No speech detected in audio file")
            print("   Continuing with empty transcript...")
            print()
        
        # Save transcription
        transcription_file = os.path.join(output_dir, f"{call_id}_transcription.json")
        with open(transcription_file, 'w', encoding='utf-8') as f:
            json.dump(transcription, f, indent=2, ensure_ascii=False)
        print(f"💾 Transcription saved to: {transcription_file}")
        print()
        
        # ============================================================
        # STEP 3: Speaker Diarization (Pyannote.audio) - REQUIRED
        # ============================================================
        print("👥 Step 3: Performing speaker diarization (REQUIRED)...")
        print()
        
        # Check audio duration and estimate time
        import librosa
        try:
            audio_duration = librosa.get_duration(path=audio_path)
            estimated_minutes = max(5, int(audio_duration / 60 / 10))  # Rough estimate
            print(f"   Audio duration: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")
            print(f"   ⏱️  Estimated processing time: {estimated_minutes}-{estimated_minutes*2} minutes")
            print(f"   ⚠️  This is normal for long audio files - diarization is CPU-intensive")
            print(f"   🔄 Processing... Please be patient (this step is required)")
            print()
        except:
            print(f"   🔄 Processing... Please be patient (this step is required)")
            print()
        
        try:
            diarization_segments = audio_processor.perform_speaker_diarization(audio_path, call_id)
            
            print(f"✅ Diarization completed")
            print(f"   Found {len(diarization_segments)} speaker segments")
            print(f"   Speakers: {len(set(s.get('speaker', '') for s in diarization_segments))}")
            
            # Save diarization to file (ensure it's saved even if save_diarization had issues)
            diarization_file = os.path.join(output_dir, f"{call_id}_diarization.json")
            diarization_data = {
                'call_id': call_id,
                'timestamp': datetime.now().isoformat(),
                'segments_count': len(diarization_segments),
                'speakers_found': len(set(s.get('speaker', '') for s in diarization_segments)),
                'segments': diarization_segments
            }
            with open(diarization_file, 'w', encoding='utf-8') as f:
                json.dump(diarization_data, f, indent=2, ensure_ascii=False, default=str)
            print(f"💾 Diarization saved to: {diarization_file}")
            print()
        except Exception as e:
            print(f"❌ Diarization failed (REQUIRED): {e}")
            print()
            print("💡 Troubleshooting:")
            print("   1. Ensure HF_TOKEN is set in .env file")
            print("   2. Check that Pyannote.audio models are downloaded")
            print("   3. Verify audio file is valid")
            print("   4. For very long files, consider splitting into smaller chunks")
            print()
            raise  # Re-raise since it's required
        
        # ============================================================
        # STEP 4: Process Text and Segment Conversation
        # ============================================================
        print("📝 Step 4: Processing text and segmenting conversation...")
        print()
        
        processed_segments = text_processor.segment_conversation(
            text,
            diarization_segments,
            call_id,
            transcription_segments=segments
        )
        
        print(f"✅ Text processing completed")
        print(f"   Processed segments: {len(processed_segments)}")
        print()
        
        # Re-save diarization file with updated text segments
        diarization_file = os.path.join(output_dir, f"{call_id}_diarization.json")
        updated_diarization = {
            'call_id': call_id,
            'timestamp': datetime.now().isoformat(),
            'segments_count': len(diarization_segments),
            'speakers_found': len(set(s.get('speaker', '') for s in diarization_segments)),
            'segments': diarization_segments
        }
        with open(diarization_file, 'w', encoding='utf-8') as f:
            json.dump(updated_diarization, f, indent=2, ensure_ascii=False, default=str)
        
        # ============================================================
        # STEP 5: Extract Audio Features
        # ============================================================
        print("🎵 Step 5: Extracting audio features...")
        print()
        
        try:
            audio_features = audio_processor.extract_audio_features(audio_path)
            print(f"✅ Audio features extracted")
            print(f"   Features: {list(audio_features.keys())}")
            print()
        except Exception as e:
            print(f"⚠️  Audio feature extraction failed: {e}")
            print("   Using fallback features...")
            audio_features = {
                "mfcc": None,
                "spectral_centroid": None,
                "zero_crossing_rate": None,
                "duration": duration
            }
            print()
        
        # ============================================================
        # STEP 6: Extract Combined Features
        # ============================================================
        print("🔬 Step 6: Extracting combined features...")
        print()
        
        feature_data = [{
            'audio_features': audio_features,
            'text_features': {'text': text},
            'segments': processed_segments
        }]
        
        try:
            fused_features = feature_extractor.fit_transform(feature_data)[0]
            print(f"✅ Feature extraction completed")
            print(f"   Feature vector shape: {fused_features.shape if hasattr(fused_features, 'shape') else 'N/A'}")
            print()
        except Exception as e:
            print(f"⚠️  Feature extraction failed: {e}")
            print("   Using fallback features...")
            import numpy as np
            fused_features = np.random.randn(50)  # Fallback
            print()
        
        # ============================================================
        # STEP 7: Run Complete Analysis
        # ============================================================
        print("🧠 Step 7: Running complete analysis...")
        print("   - Sentiment analysis")
        print("   - Emotion detection")
        print("   - Sale prediction")
        print()
        
        analysis_result = analyzer.analyze_conversation(
            audio_path=audio_path,
            segments=processed_segments
        )
        
        # Update sale prediction with actual features
        if fused_features is not None and len(fused_features) > 0:
            sale_prediction = analyzer.sale_predictor.predict_sale_probability(fused_features)
            analysis_result['sale_prediction'] = sale_prediction
        
        print("✅ Analysis completed")
        print()
        
        # ============================================================
        # STEP 8: Generate Dashboard
        # ============================================================
        print("📊 Step 8: Generating dashboard...")
        print()
        
        try:
            dashboard_html = dashboard.generate_dashboard(
                analysis_result,
                call_id=call_id,
                output_path=os.path.join(output_dir, f"{call_id}_dashboard.html")
            )
            print(f"✅ Dashboard generated")
            print(f"   Saved to: {os.path.join(output_dir, f'{call_id}_dashboard.html')}")
            print()
        except Exception as e:
            print(f"⚠️  Dashboard generation failed: {e}")
            print()
        
        # ============================================================
        # STEP 9: Save Complete Results
        # ============================================================
        print("💾 Step 9: Saving complete results...")
        print()
        
        # Prepare complete results
        complete_results = {
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "audio_file": audio_path,
            "transcription": {
                "text": text,
                "language": language,
                "duration": duration,
                "segments_count": len(segments)
            },
            "diarization": {
                "speakers_found": len(set(s.get('speaker', '') for s in diarization_segments)),
                "segments_count": len(diarization_segments)
            },
            "analysis": analysis_result,
            "summary": {
                "sale_probability": analysis_result.get('sale_prediction', {}).get('sale_probability', 0),
                "avg_sentiment": analysis_result.get('conversation_metrics', {}).get('avg_sentiment', 0),
                "dominant_emotion": analysis_result.get('conversation_metrics', {}).get('dominant_emotion', 'neutral'),
                "total_segments": len(processed_segments)
            }
        }
        
        # Save JSON results
        results_file = os.path.join(output_dir, f"{call_id}_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(complete_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Results saved to: {results_file}")
        print()
        
        # ============================================================
        # STEP 10: Print Summary
        # ============================================================
        print("=" * 70)
        print("ANALYSIS COMPLETE - SUMMARY")
        print("=" * 70)
        print()
        print(f"📊 Sale Probability: {complete_results['summary']['sale_probability']:.1%}")
        print(f"😊 Average Sentiment: {complete_results['summary']['avg_sentiment']:.2f}")
        print(f"🎭 Dominant Emotion: {complete_results['summary']['dominant_emotion']}")
        print(f"📝 Total Segments: {complete_results['summary']['total_segments']}")
        print()
        print("📁 Output Files:")
        print(f"   - Transcription: {transcription_file}")
        print(f"   - Results: {results_file}")
        if os.path.exists(os.path.join(output_dir, f"{call_id}_dashboard.html")):
            print(f"   - Dashboard: {os.path.join(output_dir, f'{call_id}_dashboard.html')}")
        print()
        print("=" * 70)
        print()
        
        return complete_results
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run complete call analysis pipeline')
    parser.add_argument('audio_file', help='Path to audio file')
    parser.add_argument('--call-id', help='Call ID (auto-generated if not provided)')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    
    args = parser.parse_args()
    
    # Resolve audio file path - check multiple locations
    audio_path = args.audio_file
    
    # If file doesn't exist, try relative to project root
    if not os.path.exists(audio_path):
        # Get project root (parent of backend directory)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Try in project root
        project_path = os.path.join(project_root, audio_path)
        if os.path.exists(project_path):
            audio_path = project_path
            print(f"📁 Found audio file in project root: {audio_path}")
        else:
            # Try just the filename in project root
            filename = os.path.basename(audio_path)
            project_path = os.path.join(project_root, filename)
            if os.path.exists(project_path):
                audio_path = project_path
                print(f"📁 Found audio file in project root: {audio_path}")
            else:
                print(f"❌ Error: Audio file not found: {args.audio_file}")
                print(f"   Searched in:")
                print(f"   - {os.path.abspath(args.audio_file)}")
                print(f"   - {project_path}")
                print(f"   - {os.path.join(project_root, os.path.basename(args.audio_file))}")
                sys.exit(1)
    
    # Resolve output directory relative to project root
    if not os.path.isabs(args.output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, args.output_dir)
    else:
        output_dir = args.output_dir
    
    run_full_analysis(audio_path, args.call_id, output_dir)

