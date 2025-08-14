#!/bin/bash
# GitHub Class Template Framework - Root Level Orchestrator
# Single entry point with automatic build target detection

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get repository root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
FRAMEWORK_DIR="$REPO_ROOT/framework"
CLASS_TEMPLATE_DIR="$REPO_ROOT/class_template"

# Framework orchestrator script
MANAGE_SCRIPT="$FRAMEWORK_DIR/scripts/manage.py"

# Function to load build configuration
load_build_config() {
    local build_config_file="$REPO_ROOT/build.yml"
    
    # Create build.yml from sample if it doesn't exist
    if [[ ! -f "$build_config_file" ]]; then
        if [[ -f "$REPO_ROOT/sample_build.yml" ]]; then
            echo -e "${YELLOW}📝 Creating build.yml from sample_build.yml${NC}"
            cp "$REPO_ROOT/sample_build.yml" "$build_config_file"
        else
            echo -e "${RED}❌ No build configuration found. Please create build.yml${NC}"
            exit 1
        fi
    fi
    
    # Export build config for use by other functions
    BUILD_CONFIG_FILE="$build_config_file"
}

# Function to get value from build.yml
get_build_config() {
    local key="$1"
    local default_value="$2"
    
    if [[ -f "$BUILD_CONFIG_FILE" ]]; then
        # Simple YAML parser for basic key: value pairs
        local value
        value=$(grep -E "^[[:space:]]*${key}:" "$BUILD_CONFIG_FILE" | head -1 | cut -d':' -f2- | xargs)
        if [[ -n "$value" && "$value" != "\"\"" && "$value" != "''" ]]; then
            # Remove quotes if present
            value=$(echo "$value" | sed 's/^["'\'']\|["'\'']$//g')
            echo "$value"
        else
            echo "$default_value"
        fi
    else
        echo "$default_value"
    fi
}

# Function to detect GitHub user from multiple sources
get_github_user() {
    # Try build.yml first
    local github_user
    github_user=$(get_build_config "github_username" "")
    if [[ -n "$github_user" ]]; then
        echo "$github_user"
        return
    fi
    
    # Try environment variable (CI/CD)
    if [[ -n "$GITHUB_ACTOR" ]]; then
        echo "$GITHUB_ACTOR"
        return
    fi
    
    # Try dna.yml professor_profile
    if [[ -f "$REPO_ROOT/dna.yml" ]]; then
        local professor_profile
        professor_profile=$(grep "^professor_profile:" "$REPO_ROOT/dna.yml" | cut -d':' -f2 | xargs)
        if [[ -n "$professor_profile" ]]; then
            echo "$professor_profile"
            return
        fi
    fi
    
    # Fallback to git config
    git config user.name 2>/dev/null || echo "unknown"
}

# Function to detect build target
detect_build_target() {
    # Check if target_directory is explicitly set in build.yml
    local target_dir
    target_dir=$(get_build_config "target_directory" "")
    
    if [[ -n "$target_dir" ]]; then
        # Use explicit configuration
        if [[ "$target_dir" == "professor" ]]; then
            echo "professor"
        elif [[ "$target_dir" =~ ^students/ ]]; then
            local username
            username=$(basename "$target_dir")
            echo "student:$username"
        else
            echo "professor"  # Default fallback
        fi
    else
        # Auto-detect based on GitHub user (legacy behavior)
        local github_user
        github_user=$(get_github_user)
        
        local student_dir="$REPO_ROOT/students/$github_user"
        
        if [[ -d "$student_dir" ]]; then
            echo "student:$github_user"
        else
            echo "professor"
        fi
    fi
}

# Function to get dev server port
get_dev_port() {
    local build_target="$1"
    
    # Check if custom port is configured in build.yml
    local custom_port
    custom_port=$(get_build_config "dev_server.port" "")
    if [[ -n "$custom_port" && "$custom_port" != "null" ]]; then
        echo "$custom_port"
        return
    fi
    
    # Default ports based on build target
    if [[ "$build_target" == professor ]]; then
        echo "1313"
    else
        echo "1314" 
    fi
}

# Function to get build target directory
get_build_target_dir() {
    local build_target="$1"
    if [[ "$build_target" == professor ]]; then
        echo "$REPO_ROOT/professor"
    else
        local username="${build_target#student:}"
        echo "$REPO_ROOT/students/$username"
    fi
}

# Main execution
main() {
    # Load build configuration first
    load_build_config
    
    # Validate environment
    if [[ ! -f "$MANAGE_SCRIPT" ]]; then
        echo -e "${RED}❌ Framework orchestrator not found: $MANAGE_SCRIPT${NC}"
        echo -e "${YELLOW}💡 Make sure framework extraction completed successfully${NC}"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed${NC}"
        exit 1
    fi
    
    # Detect build target
    local build_target
    build_target=$(detect_build_target)
    
    local build_target_dir
    build_target_dir=$(get_build_target_dir "$build_target")
    
    local dev_port
    dev_port=$(get_dev_port "$build_target")
    
    # Show build info
    if [[ "$build_target" == professor ]]; then
        echo -e "${BLUE}🎓 Building Professor Site${NC}"
        echo -e "${BLUE}📁 Content: professor/${NC}"
    else
        local username="${build_target#student:}"
        echo -e "${GREEN}👨‍🎓 Building Student Site${NC}"
        echo -e "${GREEN}📁 Content: students/$username/${NC}"
        echo -e "${GREEN}🎯 User: $username${NC}"
    fi
    
    echo -e "${BLUE}🌐 Dev Server Port: $dev_port${NC}"
    echo -e "${BLUE}🏗️  Output: hugo_generated/${NC}"
    echo ""
    
    # Execute framework orchestrator with context
    # Set working directory to the build target and call framework script
    cd "$build_target_dir"
    
    # Pass dev port if --dev is requested
    if [[ " $* " =~ " --dev " ]]; then
        exec python3 "$MANAGE_SCRIPT" --port="$dev_port" "$@"
    else
        exec python3 "$MANAGE_SCRIPT" "$@"
    fi
}

# Show usage if no arguments
if [[ $# -eq 0 ]]; then
    # Load build configuration for usage display
    load_build_config
    
    echo -e "${BLUE}GitHub Class Template Framework - Root Orchestrator${NC}"
    echo ""
    echo "🎯 Automatic Build Target Detection:"
    
    build_target=$(detect_build_target)
    if [[ "$build_target" == professor ]]; then
        echo -e "   ${BLUE}→ Professor site (default)${NC}"
    else
        username="${build_target#student:}"
        echo -e "   ${GREEN}→ Student site for: $username${NC}"
    fi
    echo ""
    echo "📖 Usage:"
    echo "   ./manage.sh --build              # Build static site"
    echo "   ./manage.sh --dev                # Start development server"
    echo "   ./manage.sh --build --dev        # Build and serve"
    echo "   ./manage.sh --status             # Show framework status"
    echo "   ./manage.sh --clean              # Clean generated files"
    echo ""
    echo "🔧 Advanced:"
    echo "   ./manage.sh --validate           # Validate content only"
    echo "   ./manage.sh --sync               # Sync framework updates (students)"
    echo "   ./manage.sh --deploy             # Build for production"
    echo ""
    exit 0
fi

# Run main function
main "$@"