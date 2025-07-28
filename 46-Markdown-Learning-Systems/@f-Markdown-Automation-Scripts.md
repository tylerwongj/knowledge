# @f-Markdown Automation Scripts

## 🎯 Learning Objectives
- Master automated markdown processing and manipulation techniques
- Implement efficient scripts for large-scale markdown content management
- Build sophisticated automation pipelines for documentation workflows
- Leverage scripting for consistent markdown formatting and quality assurance

## 🔧 Core Automation Strategies

### Python-Based Markdown Processing
```python
import re
import os
from pathlib import Path
import frontmatter
from markdown import markdown
from bs4 import BeautifulSoup

class MarkdownAutomator:
    def __init__(self, base_directory):
        self.base_dir = Path(base_directory)
        self.processed_files = []
        
    def batch_format_headers(self, directory_path):
        """Standardize heading formats across all markdown files"""
        for md_file in Path(directory_path).glob('**/*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Standardize heading format
            content = re.sub(r'^#{1,6}\s*(.+)', self._format_heading, content, flags=re.MULTILINE)
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.processed_files.append(str(md_file))
    
    def _format_heading(self, match):
        """Helper method for consistent heading formatting"""
        level = len(match.group().split()[0])
        title = match.group(1).strip()
        return f"{'#' * level} {title}"
    
    def generate_table_of_contents(self, markdown_content):
        """Auto-generate TOC from heading structure"""
        lines = markdown_content.split('\n')
        toc_lines = []
        
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('# ').strip()
                anchor = title.lower().replace(' ', '-').replace('[^a-zA-Z0-9-]', '')
                indent = '  ' * (level - 1)
                toc_lines.append(f"{indent}- [{title}](#{anchor})")
        
        return '\n'.join(toc_lines)
    
    def validate_links(self, directory_path):
        """Check for broken internal links across markdown files"""
        broken_links = []
        all_files = list(Path(directory_path).glob('**/*.md'))
        file_names = {f.stem for f in all_files}
        
        for md_file in all_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all internal links
            internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\.md\)', content)
            
            for link_text, link_path in internal_links:
                target_file = Path(link_path).stem
                if target_file not in file_names:
                    broken_links.append({
                        'file': str(md_file),
                        'link_text': link_text,
                        'target': link_path
                    })
        
        return broken_links
```

### Automated Content Enhancement
```python
class ContentEnhancer:
    def __init__(self):
        self.enhancement_rules = self._load_enhancement_rules()
    
    def enhance_code_blocks(self, content):
        """Add language specifications to code blocks"""
        # Detect and add language hints based on content
        def enhance_block(match):
            code_content = match.group(1)
            if 'def ' in code_content or 'import ' in code_content:
                return f"```python\n{code_content}\n```"
            elif 'function ' in code_content or 'const ' in code_content:
                return f"```javascript\n{code_content}\n```"
            elif 'public class' in code_content or 'using ' in code_content:
                return f"```csharp\n{code_content}\n```"
            return match.group(0)
        
        return re.sub(r'```\n(.*?)\n```', enhance_block, content, flags=re.DOTALL)
    
    def add_learning_metadata(self, content, difficulty="intermediate", time_estimate="30 minutes"):
        """Add standardized learning metadata to documents"""
        metadata = f"""---
difficulty: {difficulty}
estimated_time: "{time_estimate}"
last_updated: "{datetime.now().strftime('%Y-%m-%d')}"
tags: ["markdown", "learning", "documentation"]
---

"""
        if not content.startswith('---'):
            return metadata + content
        return content
    
    def optimize_for_obsidian(self, content):
        """Convert standard links to Obsidian-style wiki links"""
        # Convert [Title](file.md) to [[file|Title]]
        def convert_link(match):
            title, path = match.groups()
            filename = Path(path).stem
            return f"[[{filename}|{title}]]"
        
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\.md\)', convert_link, content)
```

## 🚀 AI/LLM Integration Opportunities

### Automated Content Generation Scripts
```yaml
AI_Integration_Workflows:
  content_expansion:
    - Outline-to-full-document conversion
    - Example generation for abstract concepts
    - Cross-reference suggestion automation
    - Learning objective creation from content
  
  quality_enhancement:
    - Grammar and style improvement automation
    - Technical accuracy validation scripts
    - Readability optimization workflows
    - SEO enhancement automation
  
  maintenance_automation:
    - Outdated content detection and flagging
    - Broken link repair suggestions
    - Content gap analysis and recommendations
    - Version comparison and migration scripts
```

### LLM-Powered Script Enhancement
```python
import openai
from typing import List, Dict

class AIMarkdownProcessor:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def enhance_content_with_ai(self, markdown_content: str, enhancement_type: str) -> str:
        """Use AI to enhance markdown content based on specified type"""
        prompts = {
            "clarity": "Improve the clarity and readability of this markdown content while maintaining all technical accuracy:",
            "examples": "Add practical, relevant examples to this markdown content to enhance understanding:",
            "structure": "Optimize the structure and organization of this markdown document:",
            "links": "Suggest internal linking opportunities within this markdown content:"
        }
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert technical writer specializing in markdown documentation."},
                {"role": "user", "content": f"{prompts.get(enhancement_type, prompts['clarity'])}\n\n{markdown_content}"}
            ],
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def generate_learning_objectives(self, content: str) -> List[str]:
        """AI-generated learning objectives from content"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract 3-5 specific, measurable learning objectives from the following content:"},
                {"role": "user", "content": content}
            ]
        )
        
        objectives = response.choices[0].message.content.strip().split('\n')
        return [obj.strip('- ') for obj in objectives if obj.strip()]
```

## 💡 Advanced Automation Workflows

### Git Integration Automation
```bash
#!/bin/bash
# markdown-maintenance.sh - Automated maintenance script

# Configuration
REPO_PATH="/path/to/knowledge/repo"
BACKUP_PATH="/path/to/backup"
LOG_FILE="markdown-maintenance.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Backup current state
backup_repo() {
    log_message "Creating backup..."
    rsync -av "$REPO_PATH/" "$BACKUP_PATH/backup-$(date +%Y%m%d-%H%M%S)/"
}

# Run markdown processing
process_markdown_files() {
    log_message "Starting markdown processing..."
    
    # Find and process all markdown files
    find "$REPO_PATH" -name "*.md" -type f | while read -r file; do
        # Format headers consistently
        sed -i 's/^##\s*\([^#]\)/## \1/g' "$file"
        sed -i 's/^###\s*\([^#]\)/### \1/g' "$file"
        
        # Fix common formatting issues
        sed -i 's/\s\+$//g' "$file"  # Remove trailing whitespace
        sed -i '/^$/N;/^\n$/d' "$file"  # Remove multiple empty lines
        
        log_message "Processed: $file"
    done
}

# Validate all links
validate_links() {
    log_message "Validating internal links..."
    python3 << 'EOF'
import os
import re
from pathlib import Path

def validate_markdown_links(directory):
    all_files = list(Path(directory).glob('**/*.md'))
    file_names = {f.stem for f in all_files}
    broken_links = []
    
    for md_file in all_files:
        with open(md_file, 'r') as f:
            content = f.read()
        
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\.md\)', content)
        for link_text, link_path in links:
            if Path(link_path).stem not in file_names:
                broken_links.append(f"{md_file}: {link_text} -> {link_path}")
    
    if broken_links:
        print("Broken links found:")
        for link in broken_links:
            print(f"  {link}")
    else:
        print("All links are valid!")

validate_markdown_links(os.environ.get('REPO_PATH', '.'))
EOF
}

# Main execution
main() {
    log_message "Starting maintenance workflow"
    backup_repo
    process_markdown_files
    validate_links
    log_message "Maintenance workflow completed"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

### Automated Publishing Pipeline
```yaml
# .github/workflows/markdown-publish.yml
name: Markdown Documentation Pipeline

on:
  push:
    branches: [ main ]
    paths: [ '**/*.md' ]

jobs:
  process-markdown:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install markdown beautifulsoup4 python-frontmatter
        pip install markdownlint-cli
    
    - name: Validate markdown
      run: |
        markdownlint **/*.md --config .markdownlint.json
    
    - name: Process and enhance markdown
      run: |
        python scripts/markdown-processor.py --directory . --enhance
    
    - name: Generate navigation
      run: |
        python scripts/generate-nav.py --output _nav.md
    
    - name: Build static site
      run: |
        python scripts/build-site.py --input . --output _site
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./_site
```

## 🔧 Specialized Automation Tools

### Obsidian Vault Maintenance
```python
class ObsidianVaultManager:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        
    def optimize_wiki_links(self):
        """Convert broken wiki links to proper format"""
        for md_file in self.vault_path.glob('**/*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix common wiki link issues
            content = re.sub(r'\[\[([^|\]]+)\|([^|\]]+)\]\]', r'[[\1|\2]]', content)  # Normalize format
            content = re.sub(r'\[\[([^|\]]+)\]\]', lambda m: f'[[{m.group(1).strip()}]]', content)  # Remove extra spaces
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def generate_moc_from_folder(self, folder_path, moc_name):
        """Auto-generate Map of Content from folder structure"""
        folder = Path(folder_path)
        moc_content = f"# {moc_name}\n\n## 📁 Contents\n\n"
        
        for md_file in sorted(folder.glob('*.md')):
            if md_file.stem != moc_name:
                title = self._extract_title(md_file)
                moc_content += f"- [[{md_file.stem}|{title}]]\n"
        
        moc_path = folder / f"{moc_name}.md"
        with open(moc_path, 'w', encoding='utf-8') as f:
            f.write(moc_content)
    
    def _extract_title(self, md_file):
        """Extract title from markdown file"""
        with open(md_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#'):
                return first_line.lstrip('# ')
        return md_file.stem.replace('-', ' ').title()
    
    def update_backlinks(self):
        """Maintain bidirectional links between related documents"""
        all_files = list(self.vault_path.glob('**/*.md'))
        link_graph = {}
        
        # Build link graph
        for md_file in all_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links = re.findall(r'\[\[([^|\]]+)(?:\|[^]]*)?\]\]', content)
            link_graph[md_file.stem] = links
        
        # Add backlinks sections
        for source_file, targets in link_graph.items():
            for target in targets:
                target_file = self.vault_path / f"{target}.md"
                if target_file.exists():
                    self._add_backlink_reference(target_file, source_file)
    
    def _add_backlink_reference(self, target_file, source_file):
        """Add backlink reference to target file"""
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        backlink_section = f"\n\n## 🔗 Referenced By\n- [[{source_file}]]\n"
        
        if "## 🔗 Referenced By" not in content:
            content += backlink_section
        elif f"[[{source_file}]]" not in content:
            content = content.replace(
                "## 🔗 Referenced By",
                f"## 🔗 Referenced By\n- [[{source_file}]]"
            )
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
```

### Batch Content Transformation
```python
class BatchTransformer:
    def __init__(self, source_dir, target_dir):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
    def convert_for_platform(self, platform="github"):
        """Convert markdown for specific platform requirements"""
        converters = {
            "github": self._convert_for_github,
            "confluence": self._convert_for_confluence,
            "notion": self._convert_for_notion,
            "obsidian": self._convert_for_obsidian
        }
        
        converter = converters.get(platform, self._convert_for_github)
        
        for md_file in self.source_dir.glob('**/*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            converted_content = converter(content)
            
            target_file = self.target_dir / md_file.relative_to(self.source_dir)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(converted_content)
    
    def _convert_for_github(self, content):
        """GitHub-specific optimizations"""
        # Convert wiki links to standard markdown links
        content = re.sub(r'\[\[([^|\]]+)(?:\|([^]]*))?\]\]', 
                        lambda m: f"[{m.group(2) or m.group(1)}]({m.group(1).replace(' ', '-').lower()}.md)", 
                        content)
        
        # Add GitHub-specific table of contents
        if "## Table of Contents" not in content:
            toc = self._generate_github_toc(content)
            content = content.replace("# ", f"# ", 1).replace("# ", f"{toc}\n\n# ", 1)
        
        return content
    
    def _convert_for_confluence(self, content):
        """Confluence-specific format conversion"""
        # Convert code blocks to Confluence code macro
        content = re.sub(r'```(\w+)\n(.*?)\n```', 
                        r'{code:\1}\n\2\n{code}', 
                        content, flags=re.DOTALL)
        
        # Convert info callouts to Confluence info macro
        content = re.sub(r'> \*\*Info\*\*: (.*)', r'{info}\1{info}', content)
        
        return content
    
    def _generate_github_toc(self, content):
        """Generate GitHub-compatible table of contents"""
        lines = content.split('\n')
        toc_lines = ["## Table of Contents\n"]
        
        for line in lines:
            if line.startswith('#') and not line.startswith('# '):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('# ').strip()
                anchor = title.lower().replace(' ', '-').replace('[^a-z0-9-]', '')
                indent = '  ' * (level - 2)
                toc_lines.append(f"{indent}- [{title}](#{anchor})")
        
        return '\n'.join(toc_lines) + '\n'
```

## 🎯 Performance and Monitoring

### Automated Quality Assurance
```python
class MarkdownQualityAnalyzer:
    def __init__(self):
        self.quality_metrics = {}
        
    def analyze_document_quality(self, file_path):
        """Comprehensive quality analysis of markdown document"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metrics = {
            'readability_score': self._calculate_readability(content),
            'structure_score': self._analyze_structure(content),
            'link_health': self._check_links(content),
            'content_completeness': self._assess_completeness(content),
            'formatting_consistency': self._check_formatting(content)
        }
        
        overall_score = sum(metrics.values()) / len(metrics)
        metrics['overall_score'] = overall_score
        
        return metrics
    
    def _calculate_readability(self, content):
        """Calculate readability score using various metrics"""
        # Remove markdown formatting for analysis
        text = re.sub(r'[#*`\[\]()]', '', content)
        
        words = len(text.split())
        sentences = len(re.findall(r'[.!?]+', text))
        
        if sentences == 0:
            return 0
        
        avg_words_per_sentence = words / sentences
        
        # Simple readability score (0-100)
        if avg_words_per_sentence <= 15:
            return 100
        elif avg_words_per_sentence <= 20:
            return 80
        elif avg_words_per_sentence <= 25:
            return 60
        else:
            return 40
    
    def generate_quality_report(self, directory_path):
        """Generate comprehensive quality report for all markdown files"""
        report = {"files": [], "summary": {}}
        
        for md_file in Path(directory_path).glob('**/*.md'):
            file_metrics = self.analyze_document_quality(md_file)
            file_metrics['file_path'] = str(md_file)
            report["files"].append(file_metrics)
        
        # Calculate summary statistics
        if report["files"]:
            avg_quality = sum(f['overall_score'] for f in report["files"]) / len(report["files"])
            report["summary"] = {
                "average_quality": avg_quality,
                "total_files": len(report["files"]),
                "high_quality_files": len([f for f in report["files"] if f['overall_score'] >= 80]),
                "needs_improvement": len([f for f in report["files"] if f['overall_score'] < 60])
            }
        
        return report
```

This comprehensive automation framework enables efficient, scalable markdown content management with intelligent processing, quality assurance, and cross-platform optimization for maximum productivity and consistency.