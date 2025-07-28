# @e-Plugin-Configuration-Automation

## 🎯 Learning Objectives
- Master automated configuration of Obsidian highlighting plugins
- Implement systematic plugin management for consistent environments
- Create automated backup and sync systems for highlighting configurations
- Develop AI-enhanced configuration optimization workflows

## 🔧 Automated Plugin Management

### Configuration File Templates
```json
// .obsidian/plugins/highlightr/data.json
{
  "highlightStyle": "custom",
  "customHighlights": {
    "critical": {
      "color": "#d9534f",
      "opacity": 0.25,
      "textColor": "#e8e8e8",
      "borderLeft": "2px solid #d9534f",
      "fontWeight": "normal"
    },
    "concept": {
      "color": "#8e44ad",
      "opacity": 0.25,
      "textColor": "#e8e8e8",
      "fontStyle": "italic",
      "fontWeight": "normal"
    },
    "implementation": {
      "color": "#4a9eff",
      "opacity": 0.25,
      "textColor": "#1e1e1e",
      "fontFamily": "monospace",
      "fontSize": "0.95em"
    },
    "performance": {
      "color": "#f0ad4e",
      "opacity": 0.3,
      "textColor": "#1e1e1e",
      "borderBottom": "2px dotted #f0ad4e"
    },
    "question": {
      "color": "#ff9800",
      "opacity": 0.2,
      "textColor": "#1e1e1e",
      "borderRadius": "10px",
      "textDecoration": "underline wavy #ff9800"
    }
  },
  "hotkeys": {
    "highlightCritical": "Ctrl+Shift+1",
    "highlightConcept": "Ctrl+Shift+2",
    "highlightImplementation": "Ctrl+Shift+3",
    "highlightPerformance": "Ctrl+Shift+4",
    "highlightQuestion": "Ctrl+Shift+5"
  },
  "autoSave": true,
  "exportOptions": {
    "includeHighlights": true,
    "preserveFormatting": true,
    "outputFormat": "markdown"
  }
}
```

### Style Settings Configuration
```json
// .obsidian/plugins/obsidian-style-settings/data.json
{
  "highlighter-settings": {
    "primary-highlight-opacity": 0.25,
    "secondary-highlight-opacity": 0.15,
    "highlight-animation-duration": 200,
    "highlight-border-radius": 3,
    "highlight-padding": "1px 2px",
    "highlight-margin": "0 1px"
  },
  "eye-comfort-settings": {
    "reduce-blue-light": true,
    "adaptive-brightness": false,
    "smooth-transitions": true,
    "minimal-contrast-mode": false
  },
  "typography-settings": {
    "line-height": 1.6,
    "letter-spacing": "0.01em",
    "word-spacing": "0.02em",
    "paragraph-spacing": "1.2em"
  },
  "color-scheme": {
    "use-custom-palette": true,
    "primary-bg": "#1e1e1e",
    "secondary-bg": "#2d2d2d",
    "accent-blue": "#4a9eff",
    "accent-green": "#5cb85c",
    "accent-red": "#d9534f",
    "accent-orange": "#f0ad4e",
    "accent-purple": "#8e44ad"
  }
}
```

### Automated Configuration Script
```javascript
// obsidian-highlight-config.js
class HighlightConfigManager {
    constructor(app) {
        this.app = app;
        this.configPath = '.obsidian/highlight-configs/';
        this.backupPath = '.obsidian/highlight-backups/';
    }

    async initializeConfigurations() {
        try {
            // Load base configuration template
            const baseConfig = await this.loadConfigTemplate();
            
            // Apply eye-friendly customizations
            const eyeComfortConfig = this.applyEyeComfortSettings(baseConfig);
            
            // Configure plugin-specific settings
            await this.configureHighlightrPlugin(eyeComfortConfig);
            await this.configureStyleSettings(eyeComfortConfig);
            await this.configureAdmonitionPlugin(eyeComfortConfig);
            
            // Set up hotkeys and automation
            await this.setupHotkeys();
            await this.enableAutoBackup();
            
            console.log('Highlighting configuration initialized successfully');
        } catch (error) {
            console.error('Configuration initialization failed:', error);
        }
    }

    async loadConfigTemplate() {
        const templatePath = `${this.configPath}template.json`;
        try {
            const templateFile = await this.app.vault.adapter.read(templatePath);
            return JSON.parse(templateFile);
        } catch (error) {
            return this.getDefaultConfig();
        }
    }

    applyEyeComfortSettings(config) {
        return {
            ...config,
            highlights: {
                ...config.highlights,
                opacity: Math.min(config.highlights.opacity, 0.3),
                borderRadius: 3,
                transition: 'all 0.2s ease'
            },
            colors: {
                ...config.colors,
                saturation: 0.7, // Reduce saturation by 30%
                contrast: 0.8    // Reduce contrast by 20%
            }
        };
    }

    async configureHighlightrPlugin(config) {
        const pluginData = {
            customClasses: this.generateHighlightrClasses(config),
            hotkeys: config.hotkeys,
            autoSave: true,
            exportSettings: config.export
        };

        await this.savePluginConfig('highlightr', pluginData);
    }

    generateHighlightrClasses(config) {
        const classes = {};
        
        Object.entries(config.highlightTypes).forEach(([type, settings]) => {
            classes[type] = {
                backgroundColor: `rgba(${this.hexToRgb(settings.color)}, ${settings.opacity})`,
                color: settings.textColor,
                borderLeft: settings.borderLeft || 'none',
                fontStyle: settings.fontStyle || 'normal',
                fontWeight: settings.fontWeight || 'normal',
                fontFamily: settings.fontFamily || 'inherit',
                fontSize: settings.fontSize || 'inherit',
                borderRadius: settings.borderRadius || '3px',
                padding: settings.padding || '1px 2px',
                transition: 'all 0.2s ease'
            };
        });

        return classes;
    }

    async setupHotkeys() {
        const hotkeys = [
            { key: 'Ctrl+Shift+1', action: 'highlight-critical' },
            { key: 'Ctrl+Shift+2', action: 'highlight-concept' },
            { key: 'Ctrl+Shift+3', action: 'highlight-implementation' },
            { key: 'Ctrl+Shift+4', action: 'highlight-performance' },
            { key: 'Ctrl+Shift+5', action: 'highlight-question' },
            { key: 'Ctrl+Shift+C', action: 'clear-highlights' },
            { key: 'Ctrl+Shift+E', action: 'export-highlights' }
        ];

        for (const hotkey of hotkeys) {
            await this.registerHotkey(hotkey.key, hotkey.action);
        }
    }

    async enableAutoBackup() {
        // Schedule automatic backup every hour
        setInterval(async () => {
            await this.createConfigBackup();
        }, 3600000); // 1 hour in milliseconds

        // Create backup on vault close
        this.app.workspace.on('quit', () => {
            this.createConfigBackup();
        });
    }

    async createConfigBackup() {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const backupFileName = `highlight-config-${timestamp}.json`;
        
        try {
            const currentConfig = await this.exportCurrentConfig();
            await this.app.vault.adapter.write(
                `${this.backupPath}${backupFileName}`,
                JSON.stringify(currentConfig, null, 2)
            );
            
            // Keep only last 10 backups
            await this.cleanupOldBackups();
        } catch (error) {
            console.error('Backup creation failed:', error);
        }
    }

    async cleanupOldBackups() {
        try {
            const backupFiles = await this.app.vault.adapter.list(this.backupPath);
            const sortedBackups = backupFiles.files
                .filter(file => file.includes('highlight-config-'))
                .sort((a, b) => b.localeCompare(a)) // Sort by name (timestamp)
                .slice(10); // Keep only first 10, remove rest

            for (const oldBackup of sortedBackups) {
                await this.app.vault.adapter.remove(oldBackup);
            }
        } catch (error) {
            console.error('Backup cleanup failed:', error);
        }
    }

    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result 
            ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
            : '0, 0, 0';
    }

    getDefaultConfig() {
        return {
            highlightTypes: {
                critical: { color: '#d9534f', opacity: 0.25, textColor: '#e8e8e8' },
                concept: { color: '#8e44ad', opacity: 0.25, textColor: '#e8e8e8' },
                implementation: { color: '#4a9eff', opacity: 0.25, textColor: '#1e1e1e' },
                performance: { color: '#f0ad4e', opacity: 0.3, textColor: '#1e1e1e' },
                question: { color: '#ff9800', opacity: 0.2, textColor: '#1e1e1e' }
            },
            hotkeys: {},
            export: { format: 'markdown', includeMetadata: true }
        };
    }
}
```

### Bulk Configuration Deployment
```bash
#!/bin/bash
# deploy-highlight-config.sh

# Configuration deployment script for multiple Obsidian vaults

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_SOURCE="$SCRIPT_DIR/highlight-configs"
VAULTS_DIR="$HOME/Documents/Obsidian Vaults"

echo "🔧 Deploying highlighting configurations..."

# Function to deploy configuration to a vault
deploy_to_vault() {
    local vault_path="$1"
    local vault_name=$(basename "$vault_path")
    
    echo "📁 Processing vault: $vault_name"
    
    # Create configuration directories
    mkdir -p "$vault_path/.obsidian/plugins/highlightr"
    mkdir -p "$vault_path/.obsidian/plugins/obsidian-style-settings"
    mkdir -p "$vault_path/.obsidian/highlight-configs"
    mkdir -p "$vault_path/.obsidian/highlight-backups"
    
    # Copy configuration files
    cp "$CONFIG_SOURCE/highlightr-config.json" "$vault_path/.obsidian/plugins/highlightr/data.json"
    cp "$CONFIG_SOURCE/style-settings-config.json" "$vault_path/.obsidian/plugins/obsidian-style-settings/data.json"
    cp "$CONFIG_SOURCE/custom-css/"* "$vault_path/.obsidian/snippets/" 2>/dev/null || true
    
    # Copy configuration templates
    cp "$CONFIG_SOURCE/templates/"* "$vault_path/.obsidian/highlight-configs/" 2>/dev/null || true
    
    echo "✅ Configuration deployed to $vault_name"
}

# Find and process all Obsidian vaults
if [ -d "$VAULTS_DIR" ]; then
    for vault in "$VAULTS_DIR"/*; do
        if [ -d "$vault/.obsidian" ]; then
            deploy_to_vault "$vault"
        fi
    done
else
    echo "❌ Vaults directory not found: $VAULTS_DIR"
    exit 1
fi

echo "🎉 Highlighting configuration deployment completed!"
```

### Automated Sync Script
```python
#!/usr/bin/env python3
# sync-highlight-configs.py

import os
import json
import shutil
import datetime
from pathlib import Path

class HighlightConfigSync:
    def __init__(self):
        self.home_dir = Path.home()
        self.obsidian_dir = self.home_dir / "Documents" / "Obsidian Vaults"
        self.master_config_dir = self.home_dir / ".config" / "obsidian-highlights"
        self.backup_dir = self.master_config_dir / "backups"
        
    def sync_configurations(self):
        """Sync highlighting configurations across all vaults"""
        print("🔄 Starting configuration sync...")
        
        # Ensure master config directory exists
        self.master_config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all vaults
        vaults = self.find_obsidian_vaults()
        
        if not vaults:
            print("❌ No Obsidian vaults found")
            return
            
        # Create backup before sync
        self.create_sync_backup(vaults)
        
        # Load master configuration
        master_config = self.load_master_config()
        
        # Sync to all vaults
        for vault in vaults:
            self.sync_vault_config(vault, master_config)
            
        print("✅ Configuration sync completed!")
        
    def find_obsidian_vaults(self):
        """Find all Obsidian vaults"""
        vaults = []
        
        if self.obsidian_dir.exists():
            for item in self.obsidian_dir.iterdir():
                if item.is_dir() and (item / ".obsidian").exists():
                    vaults.append(item)
                    
        return vaults
        
    def load_master_config(self):
        """Load master configuration template"""
        master_file = self.master_config_dir / "master-config.json"
        
        if master_file.exists():
            with open(master_file, 'r') as f:
                return json.load(f)
        else:
            # Create default master config
            default_config = self.create_default_config()
            with open(master_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
            
    def create_default_config(self):
        """Create default highlighting configuration"""
        return {
            "version": "1.0.0",
            "lastUpdated": datetime.datetime.now().isoformat(),
            "highlightr": {
                "customClasses": {
                    "critical": {
                        "backgroundColor": "rgba(217, 83, 79, 0.25)",
                        "color": "#e8e8e8",
                        "borderLeft": "2px solid #d9534f"
                    },
                    "concept": {
                        "backgroundColor": "rgba(142, 68, 173, 0.25)",
                        "color": "#e8e8e8",
                        "fontStyle": "italic"
                    },
                    "implementation": {
                        "backgroundColor": "rgba(74, 158, 255, 0.25)",
                        "color": "#1e1e1e",
                        "fontFamily": "monospace"
                    }
                }
            },
            "styleSettings": {
                "highlightOpacity": 0.25,
                "animationDuration": 200,
                "borderRadius": 3
            },
            "hotkeys": {
                "highlightCritical": "Ctrl+Shift+1",
                "highlightConcept": "Ctrl+Shift+2",
                "highlightImplementation": "Ctrl+Shift+3"
            }
        }
        
    def sync_vault_config(self, vault_path, master_config):
        """Sync configuration to a specific vault"""
        vault_name = vault_path.name
        print(f"📁 Syncing {vault_name}...")
        
        try:
            # Update Highlightr plugin config
            highlightr_config_path = vault_path / ".obsidian" / "plugins" / "highlightr" / "data.json"
            if highlightr_config_path.parent.exists():
                with open(highlightr_config_path, 'w') as f:
                    json.dump(master_config["highlightr"], f, indent=2)
                    
            # Update Style Settings config
            style_config_path = vault_path / ".obsidian" / "plugins" / "obsidian-style-settings" / "data.json"
            if style_config_path.parent.exists():
                with open(style_config_path, 'w') as f:
                    json.dump(master_config["styleSettings"], f, indent=2)
                    
            print(f"✅ {vault_name} synced successfully")
            
        except Exception as e:
            print(f"❌ Failed to sync {vault_name}: {e}")
            
    def create_sync_backup(self, vaults):
        """Create backup before syncing"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = self.backup_dir / f"sync_backup_{timestamp}"
        backup_folder.mkdir(exist_ok=True)
        
        for vault in vaults:
            vault_backup = backup_folder / vault.name
            vault_backup.mkdir(exist_ok=True)
            
            # Backup highlight-related configs
            config_files = [
                ".obsidian/plugins/highlightr/data.json",
                ".obsidian/plugins/obsidian-style-settings/data.json"
            ]
            
            for config_file in config_files:
                source = vault / config_file
                if source.exists():
                    dest = vault_backup / config_file
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                    
        print(f"💾 Backup created: {backup_folder}")

if __name__ == "__main__":
    sync_manager = HighlightConfigSync()
    sync_manager.sync_configurations()
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Configuration Optimization
```
"Analyze my highlighting usage patterns and optimize plugin configurations"
"Generate automated deployment script for highlighting configs across multiple vaults"
"Create adaptive highlighting settings based on content type and time of day"
```

### Smart Backup Systems
- AI-powered configuration versioning with intelligent rollback
- Automated conflict resolution for configuration changes
- Predictive backup scheduling based on usage patterns

### Performance Monitoring
- Automated performance analysis of highlighting plugin configurations
- Resource usage optimization recommendations
- Plugin compatibility monitoring and updates

## 💡 Key Highlights

### Automation Benefits
- **Consistent Environment**: Same highlighting experience across all vaults
- **Time Savings**: Automated setup eliminates manual configuration
- **Version Control**: Systematic backup and versioning of configurations
- **Scalability**: Easy deployment to new vaults and devices

### Configuration Management
- **Template-Based**: Standardized configuration templates
- **Modular Design**: Separate configs for different plugin aspects
- **Eye Comfort Integration**: Automatic application of COLOR-SCHEME.md principles
- **Hotkey Standardization**: Consistent keyboard shortcuts across vaults

### Backup Strategies
- **Automated Scheduling**: Regular backups without manual intervention
- **Version History**: Maintain multiple backup versions
- **Conflict Resolution**: Handle configuration conflicts gracefully
- **Recovery Options**: Easy restoration from any backup point

### Deployment Workflows
- **Multi-Vault Support**: Sync configurations across all Obsidian installations
- **Platform Independence**: Scripts work on Windows, macOS, and Linux
- **Error Handling**: Robust error detection and recovery
- **Progress Tracking**: Clear feedback during deployment processes

### Maintenance Automation
- **Update Detection**: Monitor for plugin updates and compatibility
- **Performance Monitoring**: Track configuration impact on Obsidian performance
- **Usage Analytics**: Analyze highlighting patterns for optimization
- **Health Checks**: Regular validation of configuration integrity

This automation framework ensures consistent, optimized highlighting environments across all learning contexts while minimizing manual maintenance overhead.