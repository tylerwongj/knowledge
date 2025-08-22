# @h-Workflow-Automation-Game-Development

## 🎯 Learning Objectives

- Master AI-driven workflow automation for Unity game development
- Implement intelligent build pipelines and testing automation
- Create automated asset processing and optimization systems
- Build AI-assisted code generation and review workflows

## 🔧 Core Automation Framework

### Intelligent Build Pipeline System

```python
import subprocess
import json
import os
import shutil
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class BuildTarget(Enum):
    STANDALONE_WINDOWS = "StandaloneWindows64"
    STANDALONE_MAC = "StandaloneOSX"
    STANDALONE_LINUX = "StandaloneLinux64"
    ANDROID = "Android"
    IOS = "iOS"
    WEBGL = "WebGL"

class BuildStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BuildConfiguration:
    target: BuildTarget
    development_build: bool = False
    script_debugging: bool = False
    run_tests: bool = True
    enable_profiler: bool = False
    compression_level: str = "standard"
    custom_defines: List[str] = None
    scenes_to_build: List[str] = None
    
    def __post_init__(self):
        if self.custom_defines is None:
            self.custom_defines = []
        if self.scenes_to_build is None:
            self.scenes_to_build = []

class UnityAutomationPipeline:
    def __init__(self, project_path: str, unity_executable: str = None):
        self.project_path = project_path
        self.unity_executable = unity_executable or self._find_unity_executable()
        self.logger = self._setup_logging()
        self.build_history: List[Dict] = []
        
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("UnityAutomation")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(
            os.path.join(self.project_path, "Logs", f"automation_{datetime.now().strftime('%Y%m%d')}.log")
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _find_unity_executable(self) -> str:
        """Auto-detect Unity executable path"""
        common_paths = [
            "/Applications/Unity/Hub/Editor/*/Unity.app/Contents/MacOS/Unity",  # macOS
            "C:/Program Files/Unity/Hub/Editor/*/Editor/Unity.exe",  # Windows
            "/opt/unity/Editor/Unity",  # Linux
        ]
        
        for path_pattern in common_paths:
            import glob
            matches = glob.glob(path_pattern)
            if matches:
                return matches[-1]  # Return latest version
        
        raise FileNotFoundError("Unity executable not found. Please specify manually.")
    
    def analyze_project_changes(self) -> Dict:
        """AI-powered analysis of project changes to determine build requirements"""
        
        # Get git changes since last build
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            changed_files = []
        
        analysis = {
            "requires_build": False,
            "requires_tests": False,
            "affected_platforms": [],
            "estimated_build_time": 0,
            "priority": "low",
            "changed_files": changed_files,
            "change_categories": []
        }
        
        # Analyze file changes
        for file_path in changed_files:
            if file_path.endswith(('.cs', '.js', '.boo')):
                analysis["requires_build"] = True
                analysis["requires_tests"] = True
                analysis["change_categories"].append("scripts")
                
            elif file_path.endswith(('.prefab', '.unity', '.asset')):
                analysis["requires_build"] = True
                analysis["change_categories"].append("assets")
                
            elif file_path.endswith(('.shader', '.compute')):
                analysis["requires_build"] = True
                analysis["affected_platforms"].extend(["StandaloneWindows64", "Android", "iOS"])
                analysis["change_categories"].append("shaders")
                
            elif 'StreamingAssets' in file_path or 'Resources' in file_path:
                analysis["requires_build"] = True
                analysis["change_categories"].append("resources")
        
        # Calculate priority and estimated build time
        if "scripts" in analysis["change_categories"]:
            analysis["priority"] = "high"
            analysis["estimated_build_time"] = 15  # minutes
        elif "shaders" in analysis["change_categories"]:
            analysis["priority"] = "medium"
            analysis["estimated_build_time"] = 10
        elif analysis["change_categories"]:
            analysis["priority"] = "medium"
            analysis["estimated_build_time"] = 8
        else:
            analysis["estimated_build_time"] = 5
        
        self.logger.info(f"Project analysis: {analysis}")
        return analysis
    
    def execute_build(self, config: BuildConfiguration) -> Dict:
        """Execute Unity build with comprehensive logging and error handling"""
        
        build_id = f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        build_output_path = os.path.join(self.project_path, "Builds", config.target.value)
        
        build_record = {
            "id": build_id,
            "target": config.target.value,
            "start_time": datetime.now().isoformat(),
            "status": BuildStatus.IN_PROGRESS.value,
            "config": config.__dict__,
            "output_path": build_output_path,
            "logs": []
        }
        
        try:
            # Ensure build directory exists
            os.makedirs(build_output_path, exist_ok=True)
            
            # Construct Unity command
            unity_args = [
                self.unity_executable,
                "-projectPath", self.project_path,
                "-buildTarget", config.target.value,
                "-buildPath", build_output_path,
                "-batchmode",
                "-quit",
                "-logFile", os.path.join(self.project_path, "Logs", f"{build_id}.log")
            ]
            
            # Add configuration options
            if config.development_build:
                unity_args.extend(["-development"])
            
            if config.script_debugging:
                unity_args.extend(["-allowDebugging"])
            
            if config.custom_defines:
                unity_args.extend(["-define", ";".join(config.custom_defines)])
            
            # Execute build
            self.logger.info(f"Starting build {build_id} for {config.target.value}")
            build_record["command"] = " ".join(unity_args)
            
            result = subprocess.run(
                unity_args,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            build_record["return_code"] = result.returncode
            build_record["stdout"] = result.stdout
            build_record["stderr"] = result.stderr
            
            if result.returncode == 0:
                build_record["status"] = BuildStatus.SUCCESS.value
                self.logger.info(f"Build {build_id} completed successfully")
                
                # Run post-build analysis
                self._analyze_build_output(build_record)
                
            else:
                build_record["status"] = BuildStatus.FAILED.value
                self.logger.error(f"Build {build_id} failed with return code {result.returncode}")
                self._analyze_build_errors(build_record)
            
        except subprocess.TimeoutExpired:
            build_record["status"] = BuildStatus.FAILED.value
            build_record["error"] = "Build timeout exceeded"
            self.logger.error(f"Build {build_id} timed out")
            
        except Exception as e:
            build_record["status"] = BuildStatus.FAILED.value
            build_record["error"] = str(e)
            self.logger.error(f"Build {build_id} failed with exception: {e}")
        
        finally:
            build_record["end_time"] = datetime.now().isoformat()
            build_record["duration"] = (
                datetime.fromisoformat(build_record["end_time"]) - 
                datetime.fromisoformat(build_record["start_time"])
            ).total_seconds()
            
            self.build_history.append(build_record)
            self._save_build_history()
        
        return build_record
    
    def _analyze_build_output(self, build_record: Dict):
        """Analyze successful build output for optimization opportunities"""
        
        # Check build size
        output_path = build_record["output_path"]
        if os.path.exists(output_path):
            total_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(output_path)
                for filename in filenames
            )
            
            build_record["build_size_mb"] = total_size / (1024 * 1024)
            
            # Size optimization suggestions
            if build_record["build_size_mb"] > 100:  # 100MB threshold
                build_record["optimization_suggestions"] = [
                    "Consider texture compression optimization",
                    "Review asset bundle usage",
                    "Check for unused assets",
                    "Optimize audio compression settings"
                ]
    
    def _analyze_build_errors(self, build_record: Dict):
        """AI-powered build error analysis with suggested fixes"""
        
        error_text = build_record.get("stderr", "") + build_record.get("stdout", "")
        
        # Common error patterns and suggestions
        error_patterns = {
            "CS0246": "Missing assembly reference - check using statements and project references",
            "CS1061": "Method not found - verify method name and containing class",
            "BuildFailedException": "Check scene list and build settings configuration",
            "UnauthorizedAccessException": "Build path permission issues - check folder permissions",
            "IOException": "File system issues - ensure Unity and antivirus aren't conflicting"
        }
        
        suggestions = []
        for pattern, suggestion in error_patterns.items():
            if pattern in error_text:
                suggestions.append(suggestion)
        
        if suggestions:
            build_record["error_suggestions"] = suggestions
        
        # Extract specific error details
        import re
        cs_errors = re.findall(r'(CS\d+).*?error.*?at (.+?):', error_text)
        if cs_errors:
            build_record["compilation_errors"] = [
                {"code": code, "location": location} for code, location in cs_errors
            ]
    
    def run_automated_tests(self, test_categories: List[str] = None) -> Dict:
        """Execute Unity Test Runner with AI-powered result analysis"""
        
        test_categories = test_categories or ["EditMode", "PlayMode"]
        test_results = {
            "start_time": datetime.now().isoformat(),
            "categories": {},
            "overall_status": "success",
            "failed_tests": [],
            "performance_metrics": {}
        }
        
        for category in test_categories:
            self.logger.info(f"Running {category} tests...")
            
            unity_args = [
                self.unity_executable,
                "-projectPath", self.project_path,
                "-runTests",
                "-testCategory", category,
                "-testResults", os.path.join(self.project_path, "TestResults", f"{category}_results.xml"),
                "-batchmode",
                "-quit",
                "-logFile", os.path.join(self.project_path, "Logs", f"tests_{category}.log")
            ]
            
            try:
                result = subprocess.run(
                    unity_args,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minute timeout
                )
                
                category_results = {
                    "return_code": result.returncode,
                    "status": "success" if result.returncode == 0 else "failed",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
                # Parse test results XML if available
                results_file = os.path.join(self.project_path, "TestResults", f"{category}_results.xml")
                if os.path.exists(results_file):
                    category_results.update(self._parse_test_results(results_file))
                
                test_results["categories"][category] = category_results
                
                if result.returncode != 0:
                    test_results["overall_status"] = "failed"
                
            except subprocess.TimeoutExpired:
                test_results["categories"][category] = {
                    "status": "timeout",
                    "error": "Test execution timeout"
                }
                test_results["overall_status"] = "failed"
        
        test_results["end_time"] = datetime.now().isoformat()
        
        # Generate test insights
        self._generate_test_insights(test_results)
        
        return test_results
    
    def _parse_test_results(self, results_file: str) -> Dict:
        """Parse Unity Test Runner XML results"""
        
        import xml.etree.ElementTree as ET
        
        try:
            tree = ET.parse(results_file)
            root = tree.getroot()
            
            results = {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "execution_time": 0.0,
                "test_details": []
            }
            
            for test_case in root.findall(".//test-case"):
                results["total_tests"] += 1
                
                status = test_case.get("result", "Unknown")
                if status == "Passed":
                    results["passed_tests"] += 1
                elif status == "Failed":
                    results["failed_tests"] += 1
                else:
                    results["skipped_tests"] += 1
                
                # Parse execution time
                time_str = test_case.get("time", "0")
                try:
                    results["execution_time"] += float(time_str)
                except ValueError:
                    pass
                
                # Store test details
                test_detail = {
                    "name": test_case.get("name", "Unknown"),
                    "status": status,
                    "time": float(time_str) if time_str.replace(".", "").isdigit() else 0.0
                }
                
                # Extract failure details
                failure = test_case.find("failure")
                if failure is not None:
                    test_detail["failure_message"] = failure.find("message").text if failure.find("message") is not None else ""
                    test_detail["stack_trace"] = failure.find("stack-trace").text if failure.find("stack-trace") is not None else ""
                
                results["test_details"].append(test_detail)
            
            return results
            
        except ET.ParseError as e:
            return {"parse_error": f"Failed to parse test results: {e}"}
    
    def _generate_test_insights(self, test_results: Dict):
        """Generate AI-powered insights from test results"""
        
        insights = []
        
        for category, results in test_results["categories"].items():
            if "failed_tests" in results and results["failed_tests"] > 0:
                insights.append(f"{category}: {results['failed_tests']} tests failed - review for regressions")
            
            if "execution_time" in results and results["execution_time"] > 300:  # 5 minutes
                insights.append(f"{category}: Tests taking {results['execution_time']:.1f}s - consider optimization")
            
            # Analyze failure patterns
            if "test_details" in results:
                failure_patterns = {}
                for test in results["test_details"]:
                    if test["status"] == "Failed" and "failure_message" in test:
                        # Simple pattern matching
                        if "NullReferenceException" in test["failure_message"]:
                            failure_patterns["null_reference"] = failure_patterns.get("null_reference", 0) + 1
                        elif "AssertionException" in test["failure_message"]:
                            failure_patterns["assertion"] = failure_patterns.get("assertion", 0) + 1
                
                for pattern, count in failure_patterns.items():
                    if count > 1:
                        insights.append(f"Multiple {pattern} failures detected - check common code paths")
        
        test_results["insights"] = insights
    
    def optimize_build_settings(self, target_platform: BuildTarget) -> Dict:
        """AI-powered build settings optimization"""
        
        optimization_settings = {
            "platform": target_platform.value,
            "recommended_settings": {},
            "rationale": []
        }
        
        # Platform-specific optimizations
        if target_platform == BuildTarget.ANDROID:
            optimization_settings["recommended_settings"] = {
                "compression": "LZ4HC",
                "texture_compression": "ASTC",
                "scripting_backend": "IL2CPP",
                "target_architectures": ["ARM64"],
                "gradle_template": True
            }
            optimization_settings["rationale"] = [
                "LZ4HC provides good compression with fast decompression",
                "ASTC texture compression is optimal for mobile GPUs",
                "IL2CPP backend provides better performance",
                "ARM64 architecture is required for Google Play"
            ]
            
        elif target_platform == BuildTarget.IOS:
            optimization_settings["recommended_settings"] = {
                "compression": "LZ4",
                "scripting_backend": "IL2CPP",
                "strip_engine_code": True,
                "optimize_mesh_data": True,
                "prebake_collision_meshes": True
            }
            optimization_settings["rationale"] = [
                "LZ4 compression balances size and performance",
                "IL2CPP is required for iOS",
                "Code stripping reduces build size",
                "Mesh optimization improves loading times"
            ]
            
        elif target_platform == BuildTarget.WEBGL:
            optimization_settings["recommended_settings"] = {
                "compression": "Gzip",
                "code_optimization": "Size",
                "strip_engine_code": True,
                "exceptions": "None",
                "name_files_as_hashes": True
            }
            optimization_settings["rationale"] = [
                "Gzip compression is optimal for web delivery",
                "Size optimization reduces download time",
                "Exception handling adds overhead in WebGL",
                "Hash-based naming enables better caching"
            ]
        
        return optimization_settings
    
    def _save_build_history(self):
        """Save build history to JSON file"""
        history_file = os.path.join(self.project_path, "Logs", "build_history.json")
        
        # Keep only last 100 builds
        history_to_save = self.build_history[-100:] if len(self.build_history) > 100 else self.build_history
        
        try:
            with open(history_file, 'w') as f:
                json.dump(history_to_save, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save build history: {e}")

# Usage example
def main():
    # Initialize automation pipeline
    pipeline = UnityAutomationPipeline("/path/to/unity/project")
    
    # Analyze project changes
    changes = pipeline.analyze_project_changes()
    
    if changes["requires_build"]:
        # Configure build based on analysis
        config = BuildConfiguration(
            target=BuildTarget.STANDALONE_WINDOWS,
            development_build=changes["priority"] == "high",
            run_tests=changes["requires_tests"]
        )
        
        # Execute build
        build_result = pipeline.execute_build(config)
        
        if build_result["status"] == BuildStatus.SUCCESS.value:
            print(f"Build completed successfully in {build_result['duration']:.1f} seconds")
            
            # Run tests if needed
            if config.run_tests:
                test_results = pipeline.run_automated_tests()
                print(f"Tests completed: {test_results['overall_status']}")
        else:
            print(f"Build failed: {build_result.get('error', 'Unknown error')}")
            if "error_suggestions" in build_result:
                print("Suggested fixes:", build_result["error_suggestions"])

if __name__ == "__main__":
    main()
```

### Asset Processing Automation

```python
import os
import json
import shutil
from PIL import Image
from typing import Dict, List, Tuple
import subprocess

class UnityAssetProcessor:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.assets_path = os.path.join(project_path, "Assets")
        self.processing_rules = self._load_processing_rules()
        
    def _load_processing_rules(self) -> Dict:
        """Load asset processing rules from configuration"""
        rules_file = os.path.join(self.project_path, "AssetProcessingRules.json")
        
        default_rules = {
            "textures": {
                "max_size": 2048,
                "compression_quality": 80,
                "formats": {
                    "ui": "RGBA32",
                    "sprite": "RGBA32",
                    "environment": "DXT5"
                },
                "auto_resize": True,
                "generate_mipmaps": True
            },
            "audio": {
                "compression": "Vorbis",
                "quality": 70,
                "force_mono": False,
                "sample_rate": 44100
            },
            "models": {
                "import_materials": False,
                "import_animations": True,
                "optimize_mesh": True,
                "weld_vertices": True,
                "compress_mesh": True
            }
        }
        
        if os.path.exists(rules_file):
            with open(rules_file, 'r') as f:
                return json.load(f)
        else:
            with open(rules_file, 'w') as f:
                json.dump(default_rules, f, indent=2)
            return default_rules
    
    def process_new_assets(self) -> Dict:
        """Automatically process newly added assets"""
        
        # Find new assets using git
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=A", "HEAD~1", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            new_files = [f for f in result.stdout.strip().split('\n') 
                        if f.startswith('Assets/') and f.strip()]
        except:
            new_files = []
        
        processing_results = {
            "processed_files": [],
            "skipped_files": [],
            "errors": [],
            "optimizations": []
        }
        
        for file_path in new_files:
            full_path = os.path.join(self.project_path, file_path)
            
            if not os.path.exists(full_path):
                continue
                
            try:
                result = self._process_asset_file(full_path)
                processing_results["processed_files"].append({
                    "file": file_path,
                    "result": result
                })
                
                if result.get("optimized"):
                    processing_results["optimizations"].append(result)
                    
            except Exception as e:
                processing_results["errors"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return processing_results
    
    def _process_asset_file(self, file_path: str) -> Dict:
        """Process individual asset file based on type"""
        
        file_ext = os.path.splitext(file_path)[1].lower()
        result = {"file": file_path, "optimized": False, "actions": []}
        
        if file_ext in ['.png', '.jpg', '.jpeg', '.tga', '.psd']:
            result.update(self._process_texture(file_path))
            
        elif file_ext in ['.wav', '.mp3', '.ogg', '.aif']:
            result.update(self._process_audio(file_path))
            
        elif file_ext in ['.fbx', '.obj', '.dae', '.3ds']:
            result.update(self._process_model(file_path))
            
        elif file_ext == '.prefab':
            result.update(self._analyze_prefab(file_path))
        
        return result
    
    def _process_texture(self, texture_path: str) -> Dict:
        """AI-powered texture optimization"""
        
        rules = self.processing_rules["textures"]
        result = {"actions": [], "original_size": 0, "optimized_size": 0}
        
        try:
            with Image.open(texture_path) as img:
                original_size = os.path.getsize(texture_path)
                result["original_size"] = original_size
                result["dimensions"] = img.size
                result["format"] = img.format
                
                # Determine optimal processing based on file path
                processing_type = self._classify_texture_type(texture_path)
                
                optimized = False
                
                # Resize if too large
                if max(img.size) > rules["max_size"]:
                    ratio = rules["max_size"] / max(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    
                    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Save optimized version
                    optimized_path = texture_path.replace('.', '_optimized.')
                    img_resized.save(optimized_path, optimize=True, quality=rules["compression_quality"])
                    
                    result["actions"].append(f"Resized from {img.size} to {new_size}")
                    result["optimized_size"] = os.path.getsize(optimized_path)
                    optimized = True
                
                # Generate .meta file suggestions
                meta_suggestions = self._generate_texture_import_settings(
                    texture_path, processing_type, img.size
                )
                result["import_suggestions"] = meta_suggestions
                
                result["optimized"] = optimized
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _classify_texture_type(self, texture_path: str) -> str:
        """Classify texture type based on file path and naming conventions"""
        
        path_lower = texture_path.lower()
        
        if 'ui/' in path_lower or '_ui' in path_lower:
            return 'ui'
        elif 'sprite' in path_lower or '_sprite' in path_lower:
            return 'sprite'
        elif 'normal' in path_lower or '_n.' in path_lower:
            return 'normal'
        elif 'environment' in path_lower or 'terrain' in path_lower:
            return 'environment'
        else:
            return 'default'
    
    def _generate_texture_import_settings(self, texture_path: str, 
                                        texture_type: str, dimensions: Tuple[int, int]) -> Dict:
        """Generate optimal Unity texture import settings"""
        
        settings = {
            "textureType": "Default",
            "maxTextureSize": min(2048, max(dimensions)),
            "compressionQuality": 50,
            "generateMipMaps": True
        }
        
        if texture_type == 'ui':
            settings.update({
                "textureType": "Sprite (2D and UI)",
                "compressionQuality": 100,
                "generateMipMaps": False,
                "filterMode": "Bilinear"
            })
            
        elif texture_type == 'normal':
            settings.update({
                "textureType": "Normal map",
                "compressionQuality": 100,
                "generateMipMaps": True
            })
            
        elif texture_type == 'environment':
            settings.update({
                "compressionQuality": 50,
                "generateMipMaps": True,
                "wrapMode": "Repeat"
            })
        
        # Platform-specific overrides
        settings["platformSettings"] = {
            "Android": {
                "format": "ASTC_6x6",
                "compressionQuality": 50
            },
            "iOS": {
                "format": "ASTC_6x6",
                "compressionQuality": 50
            },
            "Standalone": {
                "format": "DXT5",
                "compressionQuality": 100
            }
        }
        
        return settings
    
    def _process_audio(self, audio_path: str) -> Dict:
        """Process audio files with optimal settings"""
        
        rules = self.processing_rules["audio"]
        result = {"actions": [], "original_size": os.path.getsize(audio_path)}
        
        # Classify audio type
        audio_type = self._classify_audio_type(audio_path)
        
        import_settings = {
            "loadType": "Decompress On Load",
            "compressionFormat": rules["compression"],
            "quality": rules["quality"] / 100.0
        }
        
        if audio_type == 'music':
            import_settings.update({
                "loadType": "Streaming",
                "compressionFormat": "Vorbis",
                "quality": 0.7
            })
            
        elif audio_type == 'sfx':
            import_settings.update({
                "loadType": "Decompress On Load",
                "compressionFormat": "PCM",
                "quality": 1.0
            })
            
        elif audio_type == 'voice':
            import_settings.update({
                "loadType": "Compressed In Memory",
                "compressionFormat": "Vorbis",
                "quality": 0.5,
                "force_mono": True
            })
        
        result["import_suggestions"] = import_settings
        result["audio_type"] = audio_type
        
        return result
    
    def _classify_audio_type(self, audio_path: str) -> str:
        """Classify audio file type"""
        
        path_lower = audio_path.lower()
        
        if 'music' in path_lower or 'bgm' in path_lower:
            return 'music'
        elif 'voice' in path_lower or 'dialogue' in path_lower:
            return 'voice'
        elif 'sfx' in path_lower or 'sound' in path_lower:
            return 'sfx'
        else:
            return 'sfx'  # Default to SFX
    
    def _process_model(self, model_path: str) -> Dict:
        """Process 3D model files"""
        
        rules = self.processing_rules["models"]
        result = {"actions": [], "original_size": os.path.getsize(model_path)}
        
        import_settings = {
            "importMaterials": rules["import_materials"],
            "importAnimation": rules["import_animations"],
            "optimizeMesh": rules["optimize_mesh"],
            "weldVertices": rules["weld_vertices"],
            "meshCompression": "Medium" if rules["compress_mesh"] else "Off"
        }
        
        # Analyze model complexity
        model_type = self._classify_model_type(model_path)
        
        if model_type == 'character':
            import_settings.update({
                "avatarSetup": "Create From This Model",
                "animationType": "Humanoid",
                "optimizeGameObjects": True
            })
            
        elif model_type == 'environment':
            import_settings.update({
                "importAnimation": False,
                "generateColliders": True,
                "meshCompression": "High"
            })
            
        elif model_type == 'prop':
            import_settings.update({
                "importAnimation": False,
                "generateColliders": True,
                "meshCompression": "Medium"
            })
        
        result["import_suggestions"] = import_settings
        result["model_type"] = model_type
        
        return result
    
    def _classify_model_type(self, model_path: str) -> str:
        """Classify 3D model type"""
        
        path_lower = model_path.lower()
        
        if 'character' in path_lower or 'player' in path_lower or 'enemy' in path_lower:
            return 'character'
        elif 'environment' in path_lower or 'terrain' in path_lower or 'building' in path_lower:
            return 'environment'
        else:
            return 'prop'
    
    def _analyze_prefab(self, prefab_path: str) -> Dict:
        """Analyze prefab for optimization opportunities"""
        
        result = {"actions": [], "recommendations": []}
        
        # This would require parsing Unity's prefab format
        # For now, provide general recommendations
        result["recommendations"] = [
            "Check for missing script references",
            "Verify all required components are present",
            "Consider using object pooling for frequently instantiated prefabs",
            "Optimize texture references and materials"
        ]
        
        return result
    
    def generate_processing_report(self, results: Dict) -> str:
        """Generate human-readable processing report"""
        
        report = []
        report.append("# Asset Processing Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if results["processed_files"]:
            report.append("## Processed Files")
            for item in results["processed_files"]:
                report.append(f"- {item['file']}")
                if item["result"].get("optimized"):
                    report.append("  ✅ Optimized")
                for action in item["result"].get("actions", []):
                    report.append(f"  - {action}")
            report.append("")
        
        if results["optimizations"]:
            total_savings = sum(
                opt.get("original_size", 0) - opt.get("optimized_size", 0)
                for opt in results["optimizations"]
            )
            report.append(f"## Optimizations Summary")
            report.append(f"- Total files optimized: {len(results['optimizations'])}")
            report.append(f"- Total size saved: {total_savings / 1024:.1f} KB")
            report.append("")
        
        if results["errors"]:
            report.append("## Errors")
            for error in results["errors"]:
                report.append(f"- {error['file']}: {error['error']}")
            report.append("")
        
        return "\n".join(report)
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Code Generation

```
Create automated Unity development workflows:
1. AI-powered prefab generation from design specifications
2. Automated script scaffolding based on component requirements
3. Intelligent scene setup and lighting optimization
4. Smart asset naming and organization systems

Context: Unity 2022.3 LTS, team of 5-10 developers
Focus: Consistency, efficiency, reduced manual work
Requirements: Maintainable automation, clear documentation
```

### Predictive Build Optimization

```
Develop AI systems for Unity build optimization:
1. Predictive build time estimation based on project changes
2. Automated platform-specific setting recommendations
3. Intelligent asset bundle configuration optimization
4. Performance regression detection and alerting

Environment: Multi-platform Unity project, CI/CD pipeline
Goals: Faster iteration, consistent quality, reduced build failures
```

This comprehensive automation framework provides the foundation for implementing intelligent, AI-driven workflows in Unity game development, significantly reducing manual work and improving consistency across development teams.