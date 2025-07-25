# @f-Project-Organization-Systems - Intelligent Asset and Project Management

## 🎯 Learning Objectives
- Master automated project organization systems for scalable video production
- Implement intelligent file naming and folder structure automation
- Create asset tracking and version control systems for large projects
- Develop automated backup and archive workflows for long-term management

## 🔧 Automated Project Structure Creation

### Dynamic Folder Structure Generator
```python
import os
import json
from pathlib import Path
from datetime import datetime
import shutil

class ProjectStructureGenerator:
    def __init__(self, base_templates_path):
        self.templates_path = Path(base_templates_path)
        self.project_configs = self.load_project_configurations()
        
    def create_project_structure(self, project_name, project_type, client_name=None):
        """Generate standardized project folder structure"""
        
        # Standardized folder templates
        folder_structures = {
            'standard_video': {
                '01_Project_Files': {
                    'DaVinci_Resolve': [],
                    'After_Effects': [],
                    'Photoshop': [],
                    'Audio_Sessions': []
                },
                '02_Raw_Media': {
                    'Video': {
                        'Camera_A': [],
                        'Camera_B': [],
                        'Drone': [],
                        'Screen_Recording': []
                    },
                    'Audio': {
                        'Interview_Audio': [],
                        'Room_Tone': [],
                        'Music': [],
                        'SFX': []
                    }
                },
                '03_Assets': {
                    'Graphics': {
                        'Logos': [],
                        'Lower_Thirds': [],
                        'Backgrounds': [],
                        'Icons': []
                    },
                    'Stock_Media': {
                        'Stock_Video': [],
                        'Stock_Photos': [],
                        'Stock_Audio': []
                    }
                },
                '04_Exports': {
                    'Rough_Cuts': [],
                    'Client_Review': [],
                    'Final_Delivery': {
                        'Master_Files': [],
                        'Compressed': [],
                        'Archive': []
                    }
                },
                '05_Documentation': {
                    'Scripts': [],
                    'Shot_Lists': [],
                    'Edit_Notes': [],
                    'Client_Feedback': []
                }
            },
            'documentary': {
                # Extended structure for documentary projects
                '01_Pre_Production': {
                    'Research': [],
                    'Interview_Prep': [],
                    'Location_Scouting': [],
                    'Equipment_Lists': []
                },
                '02_Production': {
                    'Interview_Raw': {},
                    'B_Roll_Raw': {},
                    'Audio_Raw': {},
                    'Production_Notes': []
                },
                '03_Post_Production': {
                    'Project_Files': {},
                    'Working_Media': {},
                    'Graphics_Working': {},
                    'Audio_Working': {}
                },
                '04_Delivery': {
                    'Master_Files': [],
                    'Distribution_Formats': [],
                    'Marketing_Materials': []
                }
            }
        }
        
        # Generate project directory
        project_root = self.create_project_directory(project_name, client_name)
        
        # Create folder structure
        structure = folder_structures.get(project_type, folder_structures['standard_video'])
        self.build_folder_tree(project_root, structure)
        
        # Create project configuration file
        self.create_project_config(project_root, project_name, project_type, client_name)
        
        # Initialize tracking systems
        self.initialize_asset_tracking(project_root)
        
        return project_root
    
    def build_folder_tree(self, root_path, structure):
        """Recursively build folder structure"""
        
        for folder_name, contents in structure.items():
            folder_path = root_path / folder_name
            folder_path.mkdir(exist_ok=True)
            
            if isinstance(contents, dict):
                self.build_folder_tree(folder_path, contents)
            elif isinstance(contents, list):
                # Create placeholder files or additional setup
                if contents:
                    for item in contents:
                        (folder_path / item).mkdir(exist_ok=True)
    
    def create_project_config(self, project_path, name, type, client):
        """Create project configuration and metadata"""
        
        config = {
            'project_info': {
                'name': name,
                'type': type,
                'client': client,
                'created_date': datetime.now().isoformat(),
                'status': 'active',
                'version': '1.0'
            },
            'settings': {
                'naming_convention': self.get_naming_convention(type),
                'backup_schedule': 'daily',
                'archive_after_days': 90,
                'auto_organize': True
            },
            'team': {
                'project_manager': '',
                'editor': '',
                'colorist': '',
                'audio_engineer': ''
            }
        }
        
        with open(project_path / 'project_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
```

## 🚀 Intelligent File Organization

### Automated File Sorting System
```python
class IntelligentFileSorter:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.sorting_rules = self.load_sorting_rules()
        self.ml_classifier = self.initialize_content_classifier()
        
    def auto_organize_incoming_media(self, source_directory):
        """Automatically sort and organize incoming media files"""
        
        source_path = Path(source_directory)
        organized_files = []
        
        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                # Analyze file for optimal placement
                classification = self.classify_media_file(file_path)
                
                # Determine destination based on classification
                destination = self.determine_file_destination(classification)
                
                # Apply naming convention
                new_name = self.generate_standardized_filename(file_path, classification)
                
                # Move and rename file
                final_destination = destination / new_name
                self.move_file_safely(file_path, final_destination)
                
                organized_files.append({
                    'original': str(file_path),
                    'new_location': str(final_destination),
                    'classification': classification
                })
        
        return organized_files
    
    def classify_media_file(self, file_path):
        """AI-powered classification of media files"""
        
        file_info = {
            'extension': file_path.suffix.lower(),
            'size': file_path.stat().st_size,
            'creation_time': datetime.fromtimestamp(file_path.stat().st_ctime),
            'filename': file_path.name
        }
        
        # Analyze filename for clues
        filename_analysis = self.analyze_filename_patterns(file_path.name)
        
        # Check file metadata
        if file_info['extension'] in ['.mp4', '.mov', '.avi', '.mkv']:
            media_metadata = self.extract_video_metadata(file_path)
            content_type = self.classify_video_content(file_path, media_metadata)
        elif file_info['extension'] in ['.wav', '.mp3', '.aac', '.m4a']:
            content_type = self.classify_audio_content(file_path)
        else:
            content_type = 'unknown'
        
        return {
            'content_type': content_type,
            'media_type': self.get_media_type(file_info['extension']),
            'quality_level': self.assess_quality_level(file_path),
            'filename_patterns': filename_analysis
        }
    
    def generate_standardized_filename(self, file_path, classification):
        """Generate standardized filename based on project conventions"""
        
        # Load project naming convention
        config = self.load_project_config()
        naming_rules = config['settings']['naming_convention']
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Build filename components
        components = []
        
        if 'project_code' in naming_rules:
            components.append(naming_rules['project_code'])
        
        if classification['content_type']:
            components.append(classification['content_type'])
        
        if 'sequence_number' in naming_rules:
            sequence = self.get_next_sequence_number(classification['content_type'])
            components.append(f"{sequence:03d}")
        
        components.append(timestamp)
        
        # Combine components
        base_name = '_'.join(components)
        extension = file_path.suffix
        
        return f"{base_name}{extension}"
```

## 🔧 Asset Tracking and Version Control

### Comprehensive Asset Database
```python
import sqlite3
from datetime import datetime
import hashlib

class AssetTrackingSystem:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.db_path = self.project_root / 'asset_database.db'
        self.initialize_database()
        
    def initialize_database(self):
        """Create asset tracking database structure"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Assets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_hash TEXT UNIQUE,
                file_type TEXT,
                file_size INTEGER,
                created_date TEXT,
                modified_date TEXT,
                status TEXT DEFAULT 'active',
                version INTEGER DEFAULT 1,
                parent_asset_id INTEGER,
                metadata TEXT,
                usage_count INTEGER DEFAULT 0,
                tags TEXT
            )
        ''')
        
        # Usage tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                used_in_project TEXT,
                used_in_sequence TEXT,
                usage_date TEXT,
                usage_duration REAL,
                FOREIGN KEY (asset_id) REFERENCES assets (id)
            )
        ''')
        
        # Version history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS version_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                version_number INTEGER,
                change_description TEXT,
                changed_by TEXT,
                change_date TEXT,
                previous_filepath TEXT,
                FOREIGN KEY (asset_id) REFERENCES assets (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_asset(self, file_path, metadata=None, tags=None):
        """Register new asset in tracking system"""
        
        file_path = Path(file_path)
        
        # Calculate file hash for uniqueness
        file_hash = self.calculate_file_hash(file_path)
        
        # Extract file information
        file_info = {
            'filename': file_path.name,
            'filepath': str(file_path),
            'file_hash': file_hash,
            'file_type': file_path.suffix.lower(),
            'file_size': file_path.stat().st_size,
            'created_date': datetime.now().isoformat(),
            'modified_date': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'metadata': json.dumps(metadata) if metadata else None,
            'tags': ','.join(tags) if tags else None
        }
        
        # Insert into database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO assets (filename, filepath, file_hash, file_type, 
                                  file_size, created_date, modified_date, metadata, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_info['filename'], file_info['filepath'], file_info['file_hash'],
                file_info['file_type'], file_info['file_size'], file_info['created_date'],
                file_info['modified_date'], file_info['metadata'], file_info['tags']
            ))
            
            asset_id = cursor.lastrowid
            conn.commit()
            
            return asset_id
            
        except sqlite3.IntegrityError:
            # Asset already exists, update if needed
            return self.update_existing_asset(file_hash, file_info)
        
        finally:
            conn.close()
    
    def track_asset_usage(self, asset_id, project_context):
        """Track when and how assets are used"""
        
        usage_data = {
            'asset_id': asset_id,
            'used_in_project': project_context.get('project_name'),
            'used_in_sequence': project_context.get('sequence_name'),
            'usage_date': datetime.now().isoformat(),
            'usage_duration': project_context.get('duration', 0)
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO asset_usage (asset_id, used_in_project, used_in_sequence, 
                                   usage_date, usage_duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            usage_data['asset_id'], usage_data['used_in_project'],
            usage_data['used_in_sequence'], usage_data['usage_date'],
            usage_data['usage_duration']
        ))
        
        # Update usage count
        cursor.execute('''
            UPDATE assets SET usage_count = usage_count + 1 WHERE id = ?
        ''', (asset_id,))
        
        conn.commit()
        conn.close()
```

## 🚀 Automated Backup and Archive Systems

### Intelligent Backup Scheduler
```python
import schedule
import time
import threading
from zipfile import ZipFile
import boto3  # For cloud backups

class AutomatedBackupSystem:
    def __init__(self, project_root, backup_config):
        self.project_root = Path(project_root)
        self.config = backup_config
        self.backup_thread = None
        self.running = False
        
    def start_automated_backups(self):
        """Start automated backup scheduler"""
        
        self.running = True
        
        # Schedule different backup types
        schedule.every().hour.do(self.incremental_backup)
        schedule.every().day.at("02:00").do(self.daily_backup)
        schedule.every().week.do(self.weekly_archive)
        
        # Run scheduler in separate thread
        self.backup_thread = threading.Thread(target=self.run_scheduler)
        self.backup_thread.start()
    
    def incremental_backup(self):
        """Backup only changed files since last backup"""
        
        last_backup_time = self.get_last_backup_timestamp()
        changed_files = self.find_changed_files(last_backup_time)
        
        if changed_files:
            backup_name = f"incremental_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.create_backup_archive(changed_files, backup_name)
            
            # Upload to cloud if configured
            if self.config.get('cloud_backup_enabled'):
                self.upload_to_cloud(backup_path)
            
            self.log_backup_completion(backup_name, len(changed_files))
    
    def daily_backup(self):
        """Complete project backup daily"""
        
        backup_name = f"daily_{datetime.now().strftime('%Y%m%d')}"
        
        # Exclude certain directories from backup
        exclude_patterns = [
            '*/Cache/*',
            '*/Temp/*',
            '*/.DS_Store',
            '*/Thumbs.db'
        ]
        
        # Create comprehensive backup
        all_files = self.get_project_files(exclude_patterns)
        backup_path = self.create_backup_archive(all_files, backup_name)
        
        # Cleanup old daily backups (keep last 7)
        self.cleanup_old_backups('daily', keep_count=7)
        
        return backup_path
    
    def weekly_archive(self):
        """Create weekly project archive for long-term storage"""
        
        archive_name = f"archive_{datetime.now().strftime('%Y_week_%W')}"
        
        # Create complete project archive
        archive_path = self.create_project_archive(archive_name)
        
        # Move to long-term storage
        if self.config.get('archive_storage_path'):
            self.move_to_archive_storage(archive_path)
        
        return archive_path
    
    def create_backup_archive(self, file_list, backup_name):
        """Create compressed backup archive"""
        
        backup_dir = self.project_root / 'Backups'
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / f"{backup_name}.zip"
        
        with ZipFile(backup_path, 'w') as zipf:
            for file_path in file_list:
                # Calculate relative path for archive
                rel_path = file_path.relative_to(self.project_root)
                zipf.write(file_path, rel_path)
        
        return backup_path
    
    def upload_to_cloud(self, backup_path):
        """Upload backup to cloud storage"""
        
        if self.config['cloud_provider'] == 'aws_s3':
            s3_client = boto3.client('s3')
            bucket_name = self.config['s3_bucket']
            
            s3_key = f"project_backups/{self.project_root.name}/{backup_path.name}"
            
            try:
                s3_client.upload_file(str(backup_path), bucket_name, s3_key)
                print(f"Backup uploaded to S3: {s3_key}")
            except Exception as e:
                print(f"Cloud backup failed: {e}")
```

## 🔧 Project Status Monitoring

### Automated Project Health Checks
```python
class ProjectHealthMonitor:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.health_checks = self.initialize_health_checks()
        
    def run_comprehensive_health_check(self):
        """Run all health checks and generate report"""
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Run individual health checks
        for check_name, check_function in self.health_checks.items():
            try:
                check_result = check_function()
                health_report['checks'][check_name] = check_result
                
                if check_result['status'] == 'warning':
                    health_report['warnings'].extend(check_result['issues'])
                elif check_result['status'] == 'error':
                    health_report['errors'].extend(check_result['issues'])
                    health_report['overall_status'] = 'needs_attention'
                    
            except Exception as e:
                health_report['errors'].append(f"Health check '{check_name}' failed: {e}")
                health_report['overall_status'] = 'needs_attention'
        
        # Generate recommendations
        health_report['recommendations'] = self.generate_health_recommendations(health_report)
        
        # Save health report
        self.save_health_report(health_report)
        
        return health_report
    
    def check_storage_usage(self):
        """Monitor project storage usage"""
        
        total_size = 0
        file_count = 0
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        # Convert to readable units
        size_gb = total_size / (1024**3)
        
        status = 'healthy'
        issues = []
        
        if size_gb > 50:  # Warning at 50GB
            status = 'warning'
            issues.append(f"Large project size: {size_gb:.1f}GB")
        
        if size_gb > 100:  # Error at 100GB
            status = 'error'
            issues.append(f"Project size critical: {size_gb:.1f}GB")
        
        return {
            'status': status,
            'size_gb': size_gb,
            'file_count': file_count,
            'issues': issues
        }
    
    def check_missing_assets(self):
        """Check for missing or moved assets"""
        
        # Load asset database
        asset_tracker = AssetTrackingSystem(self.project_root)
        registered_assets = asset_tracker.get_all_assets()
        
        missing_assets = []
        
        for asset in registered_assets:
            if not Path(asset['filepath']).exists():
                missing_assets.append({
                    'filename': asset['filename'],
                    'expected_path': asset['filepath'],
                    'last_seen': asset['modified_date']
                })
        
        status = 'healthy' if not missing_assets else 'error'
        
        return {
            'status': status,
            'missing_count': len(missing_assets),
            'missing_assets': missing_assets,
            'issues': [f"Missing {len(missing_assets)} assets"] if missing_assets else []
        }
```

## 💡 Key Organization Benefits

### Efficiency Improvements
- **Project Setup**: Manual (2 hours) → Automated (5 minutes) = 95% time reduction
- **Asset Organization**: Continuous automated sorting vs. manual cleanup
- **Version Control**: Automated tracking vs. manual file management
- **Backup Systems**: Scheduled automation vs. manual backup procedures

### Scalability Features
- **Multi-Project Management**: Centralized organization system
- **Team Collaboration**: Standardized structures and naming
- **Asset Reusability**: Intelligent asset tracking and suggestions
- **Quality Assurance**: Automated health monitoring and reporting

This comprehensive project organization system transforms chaotic video production environments into systematically managed, scalable workflows that maintain consistency and efficiency across multiple projects and team members.