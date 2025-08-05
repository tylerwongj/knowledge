# @b-Blender-Unity-Asset-Pipeline

## 🎯 Learning Objectives
- Master efficient 3D asset creation workflow from Blender to Unity
- Optimize mesh topology and UV mapping for game performance
- Implement proper export settings for various asset types
- Automate repetitive pipeline tasks with scripts and add-ons

## 🔧 Core Asset Types & Workflow

### Static Meshes (Props, Environment)
```python
# Blender Python script for batch export
import bpy
import os

def export_selected_objects():
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            # Select only current object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            # Export FBX with Unity-optimized settings
            filepath = f"C:/Unity_Assets/{obj.name}.fbx"
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                use_mesh_modifiers=True,
                mesh_smooth_type='FACE',
                use_tspace=True  # Tangent space for normal maps
            )
```

### Character Models & Rigging
- **Topology Requirements**: Quads preferred, edge loops around joints
- **Polygon Count**: 2K-10K for characters depending on platform
- **Bone Hierarchy**: Root motion bone, proper naming conventions
- **Weight Painting**: Smooth deformation, test poses early

### Environment Pieces
- **Modular Design**: Snap-together pieces, consistent scale
- **Texture Atlas**: Shared materials, optimized draw calls
- **LOD Preparation**: High, medium, low poly versions

## 🎨 Material & Texture Workflow

### PBR Material Setup in Blender
```glsl
// Shader setup for Unity compatibility
Material Output:
├── Principled BSDF
    ├── Base Color → Albedo Map
    ├── Metallic → Metallic Map
    ├── Roughness → Roughness Map
    ├── Normal → Normal Map (Tangent Space)
    └── Emission → Emission Map
```

### Texture Baking Process
1. **High Poly to Low Poly Baking**
   - Cage modifiers for accurate projection
   - Normal map baking settings: Tangent space, 16-bit
   - AO baking with proper ray distance

2. **UV Mapping Best Practices**
   - Non-overlapping UVs for lightmapping
   - Proper seam placement to minimize stretching
   - Consistent texel density across objects

### Export Settings for Unity
```python
# Material export configuration
material_settings = {
    'use_mesh_modifiers': True,
    'use_custom_props': True,
    'path_mode': 'COPY',
    'embed_textures': False,  # Keep textures separate
    'bake_space_transform': True
}
```

## ⚡ Performance Optimization

### Mesh Optimization Checklist
- [ ] Remove interior faces and hidden geometry
- [ ] Merge vertices within threshold (0.01m)
- [ ] Apply scale and rotation transforms
- [ ] Check for n-gons and fix topology
- [ ] Optimize edge loops for deformation

### LOD (Level of Detail) Creation
```python
# Blender script for automatic LOD generation
def create_lod_versions(base_mesh, lod_levels=[0.75, 0.5, 0.25]):
    for i, ratio in enumerate(lod_levels):
        # Duplicate mesh
        lod_mesh = base_mesh.copy()
        lod_mesh.data = base_mesh.data.copy()
        lod_mesh.name = f"{base_mesh.name}_LOD{i+1}"
        
        # Apply decimate modifier
        decimate = lod_mesh.modifiers.new(name="Decimate", type='DECIMATE')
        decimate.ratio = ratio
        
        # Apply modifier
        bpy.context.view_layer.objects.active = lod_mesh
        bpy.ops.object.modifier_apply(modifier="Decimate")
```

## 🚀 AI/LLM Integration Opportunities

### Automated Asset Generation
- **Prompt**: "Generate Blender Python script for creating [specific asset type] with Unity-optimized settings"
- **Use Case**: Batch processing multiple assets with consistent settings
- **AI Tools**: ChatGPT for script generation, Claude for code review

### Workflow Optimization
- **Documentation Generation**: AI-generated material setup guides
- **Error Troubleshooting**: LLM assistance for export issues
- **Naming Convention Automation**: Scripts for consistent asset naming

### Learning Acceleration
```python
# AI-generated learning prompts
learning_prompts = [
    "Explain the difference between object mode and edit mode in Blender for game asset creation",
    "Generate a checklist for optimizing 3D models for mobile Unity games",
    "Create a material setup guide for PBR textures in Blender"
]
```

## 🔗 Unity Integration Setup

### Project Structure
```
Unity_Project/
├── Assets/
    ├── Models/
    │   ├── Characters/
    │   ├── Environment/
    │   └── Props/
    ├── Materials/
    │   ├── Character_Materials/
    │   └── Environment_Materials/
    └── Textures/
        ├── Albedo/
        ├── Normal/
        └── Roughness/
```

### Import Settings Template
- **Model Tab**: Scale Factor 1, Read/Write Enabled for editing
- **Rig Tab**: Animation Type based on asset (None/Generic/Humanoid)
- **Animation Tab**: Import constraints, optimize bones
- **Materials Tab**: Use External Materials for shared assets

## 💡 Key Highlights

### Critical Export Settings
- **FBX Version**: 7.4 binary for best Unity compatibility
- **Forward Axis**: -Z Forward (Blender) → Z Forward (Unity)
- **Scale**: Apply transforms before export, use consistent units
- **Smoothing**: Export smoothing groups for proper lighting

### Common Pipeline Issues
1. **Incorrect Scale**: Always apply transforms in Blender
2. **Missing Materials**: Export textures separately, link in Unity
3. **Animation Issues**: Check armature naming and bone hierarchy
4. **Normal Map Problems**: Ensure tangent space, check import settings

### Productivity Boosters
- **Add-ons**: Auto-Rig Pro, Hard Ops, Batch Operations
- **Custom Scripts**: Automated export, naming conventions
- **Templates**: Pre-configured scenes with cameras and lighting
- **Hotkey Setup**: Custom shortcuts for frequent operations

## 🎮 Game-Specific Considerations

### Mobile Game Assets
- Lower polygon counts (500-2K triangles)
- Simplified shaders, fewer texture channels
- Aggressive LOD strategies
- Texture compression considerations

### PC/Console Assets
- Higher detail allowance (5K-20K+ triangles)
- Full PBR material support
- Multiple LOD levels
- High-resolution texture support

### VR Optimization
- Extremely aggressive polygon reduction
- Simplified materials for performance
- Careful consideration of vertex density
- Baked lighting preferred over real-time

---

*Blender-Unity Pipeline v1.0 | Game Development Optimized | AI-Enhanced Workflow*