# Build and Deployment Information

## Build System

### Build Tools
- **PyInstaller**: Packages Python applications into standalone executables
- **Version**: Latest (installed via pip)
- **Build Type**: `--onefile --windowed` (single executable, no console)

### Build Scripts

#### 1. ShareProfitTracker Builds

##### build_modern_complete.bat
- **Location**: `ShareProfitTracker/`
- **Spec File**: `build_modern_comprehensive.spec`
- **Output**: Creates executable with all modern features
- **Features**: Full UI, all services, stock database

##### build_massive_2000plus.spec
- **Location**: `ShareProfitTracker/`
- **Purpose**: Build with 2000+ stock database
- **Entry Point**: Specific main file with massive stock support
- **Output**: `ShareProfitTracker_2000Plus.exe`

##### Other Build Files
- `build_exe.spec` - Basic build specification
- `build_enhanced.spec` - Enhanced features build
- `build_optimized.spec` - Optimized build with size reduction
- `build_simple.spec` - Minimal feature set
- `build_latest.spec` - Latest stable version

#### 2. ModernShareTracker Builds

##### build_ultimate_complete.bat (Root directory)
- **Location**: Project root (`D:\Projects\share mkt\`)
- **Builds From**: `ModernShareTracker/unified_share_tracker_modern.py`
- **Output**: `ShareProfitTracker_Ultimate_Complete.exe`
- **Features Included**:
  - ALL ShareProfitTracker core features
  - Enhanced tax reporting with realized gains tracking
  - AI Financial Advisor chatbot
  - Real-time price alerts and notifications
  - Advanced portfolio rebalancing engine
  - Indian tax optimization strategies
  - Ultra-fast price refresh system
  - Excel export capabilities
  - Corporate actions tracking
  - 2000+ Indian stocks database
  - Modern professional UI

##### build_modern_complete.bat
- **Location**: `ModernShareTracker/`
- **Spec File**: `build_ultimate_comprehensive.spec`
- **Output**: Modern version executable

##### build_2000plus_exe.bat
- **Location**: `ModernShareTracker/`
- **Spec File**: `ShareProfitTracker_2000Plus.spec`
- **Output**: Version with comprehensive stock database

#### 3. Build Process

##### Pre-build Steps
```batch
# Clean cache
if exist "__pycache__" rmdir /s /q "__pycache__"

# Install/update dependencies
pip install --upgrade yfinance nsepython pandas numpy openpyxl 
pip install --upgrade aiosqlite tkcalendar beautifulsoup4 lxml requests pyinstaller

# Optional AI packages
pip install --upgrade openai websocket-client
```

##### Build Command Pattern
```batch
pyinstaller --clean --onefile --windowed --name="ExecutableName" main_file.py
```

##### Post-build Steps
```batch
# Move executable from dist/ to main directory
copy "dist\ExecutableName.exe" "..\ExecutableName.exe"

# Display file size
dir "ExecutableName.exe" | find /v "Directory"
```

## PyInstaller Specifications

### Common Spec File Structure
```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main_file.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/*.json', 'data'),  # Include stock databases
        ('*.db', '.'),             # Include database files
    ],
    hiddenimports=[
        'yfinance',
        'nsepython',
        'pandas',
        # ... other dependencies
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ExecutableName',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### Build Optimization Flags
- `--onefile`: Single executable (vs directory)
- `--windowed`: No console window
- `--clean`: Clean PyInstaller cache before building
- `upx=True`: Compress executable (UPX)
- `strip=False`: Don't strip symbols (for debugging)

## Deployment

### Executable Outputs
Located in project root after successful build:

1. **ShareProfitTracker_2000Plus.exe**
   - Size: ~12.7 MB
   - Features: Core + 2000+ stocks
   - Built from: ShareProfitTracker

2. **ShareProfitTracker_Modern.exe**
   - Size: ~12.7 MB
   - Features: Core + Modern UI
   - Built from: ModernShareTracker

3. **ShareProfitTracker_Ultimate_Complete.exe**
   - Size: ~13-15 MB (estimated)
   - Features: Everything (Core + Advanced)
   - Built from: ModernShareTracker/unified_share_tracker_modern.py

### Distribution Requirements
- **Platform**: Windows 7/8/10/11 (x64)
- **RAM**: Minimum 2GB
- **Disk Space**: 100MB recommended
- **Internet**: Required for price updates
- **No Installation Required**: Portable executable

### Database Files
- Executables create database files on first run
- Database location: Same directory as executable
- Files created:
  - `portfolio.db` (for ShareProfitTracker versions)
  - `unified_portfolio.db` (for Modern versions)
  - `theme_config.json` (theme settings)

## Development Workflow

### Local Development
1. **Environment Setup**
   ```bash
   cd ShareProfitTracker  # or ModernShareTracker
   pip install -r requirements.txt
   ```

2. **Run Locally**
   ```bash
   python main.py  # ShareProfitTracker
   python run_modern_tracker.py  # ModernShareTracker
   ```

3. **Testing**
   ```bash
   python test_phase1.py
   python test_enhanced_notifications.py
   python test_2000plus_coverage.py
   ```

### Build for Distribution
1. **Choose build script** based on features needed
2. **Run build script**: `build_ultimate_complete.bat`
3. **Test executable** before distribution
4. **Verify file size** and dependencies

### Version Control
- **Git repository** present (`.git/`)
- **Recent commits**:
  - "Include all project files"
  - "Initial commit - Share Market Tracking Project"
- **Branches**: Currently on `master`
- **Ignored files**: `.gitignore` includes `__pycache__`, `.pyc`, etc.

## File Size Optimization

### Current Sizes
- Core executable: ~12-13 MB
- With UPX compression: ~6-8 MB possible
- Database files: 32-77 KB (grows with data)

### Optimization Techniques Used
1. UPX compression in spec files
2. Exclude unnecessary modules
3. Single file mode (--onefile)
4. Strip debug symbols (optional)
5. Remove test files from build

## Common Build Issues

### Missing Modules
- **Solution**: Add to `hiddenimports` in spec file
- **Example**: yfinance, nsepython dependencies

### Database Not Included
- **Solution**: Add to `datas` in spec file
- **Pattern**: `('*.db', '.')` or `('data/*.json', 'data')`

### Large File Size
- **Solutions**: 
  - Enable UPX compression
  - Exclude unnecessary packages
  - Use `--exclude-module` for unused imports
  
### Import Errors at Runtime
- **Solution**: Test locally first, check import paths
- **Fix**: Add to sys.path in main.py or use relative imports

## Backup and Recovery

### Backup Locations
- Source code: Git repository
- Databases: Manual backup recommended
- Build scripts: Versioned in git

### Recovery Procedures
1. Database corruption: Delete and recreate from schema
2. Build failures: Clean cache and rebuild
3. Lost data: Restore from CSV exports
