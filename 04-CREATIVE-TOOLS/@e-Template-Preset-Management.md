# @e-Template-Preset-Management - Systematic Template and Preset Automation

## 🎯 Learning Objectives
- Create comprehensive template libraries for instant project setup
- Develop automated preset management systems for consistent output
- Master version control and synchronization for template assets
- Implement intelligent template selection based on project requirements

## 🔧 Project Template Architecture

### Standardized Project Structure
```json
{
  "template_metadata": {
    "name": "Corporate_Interview_Template",
    "version": "2.1",
    "description": "Standard setup for corporate interview content",
    "created_date": "2024-01-15",
    "last_modified": "2024-01-20",
    "author": "Production Team",
    "tags": ["interview", "corporate", "standard"]
  },
  "project_settings": {
    "resolution": "1920x1080",
    "frame_rate": "23.98",
    "color_space": "Rec.709",
    "audio_sample_rate": "48000"
  },
  "timeline_structure": {
    "video_tracks": 4,
    "audio_tracks": 6,
    "track_naming": {
      "V1": "Main_Camera",
      "V2": "B_Roll",
      "V3": "Graphics_Lower",
      "V4": "Graphics_Upper",
      "A1": "Interview_Audio",
      "A2": "Room_Tone",
      "A3": "Music",
      "A4": "SFX"
    }
  }
}
```

### Automated Template Creation System
```python
import json
import shutil
from pathlib import Path
from datetime import datetime

class TemplateManager:
    def __init__(self, template_library_path):
        self.library_path = Path(template_library_path)
        self.templates = self.load_template_catalog()
        
    def create_template_from_project(self, project_path, template_name, 
                                   description, tags=None):
        """Create reusable template from existing project"""
        
        template_data = {
            'metadata': {
                'name': template_name,
                'version': '1.0',
                'description': description,
                'created_date': datetime.now().isoformat(),
                'tags': tags or []
            },
            'source_project': str(project_path)
        }
        
        # Analyze project structure
        project_analysis = self.analyze_project_structure(project_path)
        template_data['structure'] = project_analysis
        
        # Extract reusable assets
        template_assets = self.extract_template_assets(project_path)
        template_data['assets'] = template_assets
        
        # Save template configuration
        template_dir = self.library_path / template_name
        template_dir.mkdir(exist_ok=True)
        
        with open(template_dir / 'template.json', 'w') as f:
            json.dump(template_data, f, indent=2)
        
        # Copy template assets
        self.copy_template_assets(template_assets, template_dir)
        
        return template_data
    
    def apply_template_to_project(self, template_name, new_project_path):
        """Apply template to new project setup"""
        
        template = self.load_template(template_name)
        
        # Create project directory structure
        self.create_project_structure(new_project_path, template)
        
        # Copy template assets
        self.deploy_template_assets(template, new_project_path)
        
        # Configure project settings
        self.apply_project_settings(template, new_project_path)
        
        return f"Template '{template_name}' applied to {new_project_path}"
    
    def analyze_project_structure(self, project_path):
        """Analyze existing project for template creation"""
        
        structure = {
            'folders': [],
            'naming_conventions': {},
            'file_types': {},
            'workflow_patterns': {}
        }
        
        # Scan project directory
        for item in Path(project_path).rglob('*'):
            if item.is_dir():
                structure['folders'].append(str(item.relative_to(project_path)))
            else:
                file_type = item.suffix.lower()
                if file_type not in structure['file_types']:
                    structure['file_types'][file_type] = []
                structure['file_types'][file_type].append(str(item.name))
        
        return structure
```

## 🚀 Preset Management System

### Color Grading Preset Library
```python
class ColorGradingPresetManager:
    def __init__(self, preset_library_path):
        self.library_path = Path(preset_library_path)
        self.presets = self.load_preset_catalog()
        
    def create_color_preset(self, name, settings, metadata=None):
        """Create reusable color grading preset"""
        
        preset_data = {
            'name': name,
            'type': 'color_grading',
            'version': '1.0',
            'created_date': datetime.now().isoformat(),
            'metadata': metadata or {},
            'settings': {
                'primary_wheels': {
                    'lift': settings.get('lift', [0, 0, 0, 0]),
                    'gamma': settings.get('gamma', [1, 1, 1, 1]),
                    'gain': settings.get('gain', [1, 1, 1, 1])
                },
                'curves': {
                    'rgb_curves': settings.get('rgb_curves', {}),
                    'hue_curves': settings.get('hue_curves', {})
                },
                'qualifiers': settings.get('qualifiers', {}),
                'lut_path': settings.get('lut_path', None)
            }
        }
        
        # Save preset
        preset_file = self.library_path / f"{name}.json"
        with open(preset_file, 'w') as f:
            json.dump(preset_data, f, indent=2)
        
        return preset_data
    
    def apply_color_preset(self, preset_name, target_clips):
        """Apply color preset to selected clips"""
        
        preset = self.load_preset(preset_name)
        
        for clip in target_clips:
            self.apply_color_settings_to_clip(clip, preset['settings'])
        
        return f"Applied '{preset_name}' to {len(target_clips)} clips"
    
    def batch_create_presets_from_reference(self, reference_images):
        """Create multiple presets from reference imagery"""
        
        presets_created = []
        
        for ref_image in reference_images:
            # Analyze reference image colors
            color_analysis = self.analyze_reference_colors(ref_image)
            
            # Generate preset settings
            preset_settings = self.generate_preset_from_analysis(color_analysis)
            
            # Create preset
            preset_name = f"ref_{Path(ref_image).stem}"
            preset = self.create_color_preset(preset_name, preset_settings)
            
            presets_created.append(preset)
        
        return presets_created
```

### Audio Processing Preset System
```python
class AudioPresetManager:
    def __init__(self, preset_library_path):
        self.library_path = Path(preset_library_path)
        
    def create_audio_chain_preset(self, name, processing_chain):
        """Create reusable audio processing chain"""
        
        preset_data = {
            'name': name,
            'type': 'audio_processing',
            'chain': []
        }
        
        for processor in processing_chain:
            preset_data['chain'].append({
                'plugin': processor['plugin_name'],
                'parameters': processor['settings'],
                'bypass': processor.get('bypass', False),
                'order': processor['order']
            })
        
        # Common audio presets
        preset_templates = {
            'podcast_voice': {
                'eq': {'high_pass': 80, 'presence_boost': 3000},
                'compressor': {'ratio': 3.0, 'threshold': -18, 'attack': 3, 'release': 100},
                'noise_gate': {'threshold': -40, 'ratio': 10},
                'limiter': {'ceiling': -1, 'release': 50}
            },
            'music_master': {
                'eq': {'low_cut': 20, 'high_cut': 20000},
                'compressor': {'ratio': 2.0, 'threshold': -12, 'knee': 2},
                'stereo_imager': {'width': 110},
                'limiter': {'ceiling': -0.1, 'isr': 4}
            },
            'dialogue_cleanup': {
                'spectral_denoise': {'reduction': -20, 'sensitivity': 8},
                'eq': {'high_pass': 100, 'low_pass': 8000},
                'compressor': {'ratio': 4.0, 'threshold': -20},
                'deesser': {'frequency': 6000, 'reduction': -6}
            }
        }
        
        return preset_data
```

## 🔧 Intelligent Template Selection

### AI-Powered Template Matching
```python
class IntelligentTemplateSelector:
    def __init__(self, template_manager):
        self.template_manager = template_manager
        self.selection_model = self.initialize_selection_ai()
        
    def recommend_template(self, project_requirements):
        """AI-powered template recommendation"""
        
        selection_prompt = f"""
        Recommend the best template for this project:
        
        Project Requirements:
        - Content type: {project_requirements['content_type']}
        - Duration: {project_requirements['duration']}
        - Audience: {project_requirements['audience']}
        - Budget level: {project_requirements['budget']}
        - Delivery format: {project_requirements['delivery_format']}
        - Special requirements: {project_requirements['special_needs']}
        
        Available templates:
        {self.get_template_summaries()}
        
        Recommend top 3 templates with reasoning:
        1. Best overall match
        2. Alternative option
        3. Creative alternative
        
        Consider efficiency, quality, and requirements alignment.
        """
        
        recommendation = self.get_ai_recommendation(selection_prompt)
        
        return self.parse_template_recommendations(recommendation)
    
    def analyze_project_compatibility(self, template_name, project_specs):
        """Check template compatibility with project requirements"""
        
        template = self.template_manager.load_template(template_name)
        compatibility_score = 0
        issues = []
        
        # Check technical compatibility
        if template['project_settings']['resolution'] == project_specs['resolution']:
            compatibility_score += 25
        else:
            issues.append("Resolution mismatch")
        
        if template['project_settings']['frame_rate'] == project_specs['frame_rate']:
            compatibility_score += 25
        else:
            issues.append("Frame rate mismatch")
        
        # Check workflow compatibility
        if template['metadata']['tags']:
            matching_tags = set(template['metadata']['tags']) & set(project_specs.get('tags', []))
            compatibility_score += len(matching_tags) * 10
        
        return {
            'compatibility_score': compatibility_score,
            'issues': issues,
            'recommendation': 'suitable' if compatibility_score >= 70 else 'needs_adjustment'
        }
```

## 🚀 Version Control and Synchronization

### Template Version Management
```python
class TemplateVersionControl:
    def __init__(self, repository_path):
        self.repo_path = Path(repository_path)
        self.version_history = self.load_version_history()
        
    def create_template_version(self, template_name, changes, version_type='minor'):
        """Create new version of existing template"""
        
        current_template = self.load_current_template(template_name)
        current_version = current_template['metadata']['version']
        
        # Calculate new version number
        new_version = self.increment_version(current_version, version_type)
        
        # Create version record
        version_record = {
            'template_name': template_name,
            'version': new_version,
            'previous_version': current_version,
            'changes': changes,
            'created_date': datetime.now().isoformat(),
            'change_type': version_type
        }
        
        # Update template with new version
        updated_template = current_template.copy()
        updated_template['metadata']['version'] = new_version
        updated_template['metadata']['last_modified'] = datetime.now().isoformat()
        
        # Save new version
        self.save_template_version(template_name, updated_template, version_record)
        
        return version_record
    
    def sync_templates_across_systems(self, sync_targets):
        """Synchronize templates across multiple workstations"""
        
        sync_report = {
            'synced_templates': [],
            'conflicts': [],
            'errors': []
        }
        
        for target_system in sync_targets:
            try:
                # Compare template versions
                local_templates = self.get_local_template_manifest()
                remote_templates = self.get_remote_template_manifest(target_system)
                
                # Identify sync needs
                sync_plan = self.create_sync_plan(local_templates, remote_templates)
                
                # Execute synchronization
                sync_results = self.execute_sync_plan(sync_plan, target_system)
                sync_report['synced_templates'].extend(sync_results)
                
            except Exception as e:
                sync_report['errors'].append({
                    'target': target_system,
                    'error': str(e)
                })
        
        return sync_report
```

## 🔧 Advanced Preset Automation

### Dynamic Preset Generation
```python
class DynamicPresetGenerator:
    def __init__(self):
        self.generation_models = self.load_generation_models()
        
    def generate_presets_from_content_analysis(self, content_analysis):
        """Generate custom presets based on content characteristics"""
        
        # Analyze content for optimal settings
        if content_analysis['lighting_conditions'] == 'low_light':
            color_preset = self.generate_low_light_preset(content_analysis)
        elif content_analysis['content_type'] == 'outdoor_sports':
            color_preset = self.generate_sports_preset(content_analysis)
        else:
            color_preset = self.generate_general_preset(content_analysis)
        
        # Generate matching audio preset
        audio_preset = self.generate_audio_preset_for_content(content_analysis)
        
        return {
            'color_preset': color_preset,
            'audio_preset': audio_preset,
            'recommended_workflow': self.suggest_workflow_preset(content_analysis)
        }
    
    def generate_style_matched_presets(self, reference_media):
        """Generate presets that match reference media style"""
        
        # Analyze reference media characteristics
        style_analysis = self.analyze_reference_style(reference_media)
        
        # Generate matching presets
        preset_set = {
            'color_grading': self.create_style_matched_color_preset(style_analysis),
            'audio_processing': self.create_style_matched_audio_preset(style_analysis),
            'motion_graphics': self.create_style_matched_graphics_preset(style_analysis)
        }
        
        return preset_set
```

## 💡 Template Library Organization

### Intelligent Categorization System
```python
class TemplateLibraryOrganizer:
    def __init__(self, library_path):
        self.library_path = Path(library_path)
        self.categories = self.initialize_category_system()
        
    def auto_categorize_templates(self):
        """Automatically categorize templates based on characteristics"""
        
        categorization_rules = {
            'content_type': {
                'interview': ['interview', 'talking_head', 'conversation'],
                'documentary': ['documentary', 'narrative', 'story'],
                'corporate': ['corporate', 'business', 'professional'],
                'creative': ['creative', 'artistic', 'experimental'],
                'social_media': ['social', 'short_form', 'vertical']
            },
            'production_scale': {
                'minimal': ['single_camera', 'basic_audio', 'simple_graphics'],
                'standard': ['multi_camera', 'professional_audio', 'motion_graphics'],
                'advanced': ['complex_workflow', 'vfx', 'multi_format_delivery']
            },
            'turnaround_time': {
                'rapid': ['quick_turnaround', 'automated_workflow'],
                'standard': ['normal_workflow', 'review_cycles'],
                'extended': ['complex_review', 'multiple_revisions']
            }
        }
        
        for template in self.get_all_templates():
            categories = self.classify_template(template, categorization_rules)
            self.assign_template_categories(template['name'], categories)
        
        return self.generate_categorization_report()
```

## 🚀 Performance Optimization

### Template Performance Metrics
- **Project Setup Time**: Manual (45 min) → Template (3 min) = 93% reduction
- **Consistency Score**: Manual (65%) → Template (95%) = 46% improvement  
- **Asset Organization**: Manual sorting → Automated structure
- **Quality Assurance**: Checklist-based → Built-in validation

This comprehensive template and preset management system creates a foundation for scalable, consistent video production workflows that maintain high quality while dramatically reducing setup and configuration time across projects.