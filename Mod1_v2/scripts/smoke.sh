#!/bin/bash
#
# InterView Mod1-2-3 System Smoke Test
# Comprehensive health check and integration test
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MOD1_URL="http://localhost:8080"
MOD2_URL="http://localhost:8001"
MOD3_URL="http://localhost:9001"
SESSION_ID="smoke_test_$(date +%s)"

echo -e "${BLUE}🚀 InterView System Smoke Test${NC}"
echo -e "${BLUE}==============================${NC}"
echo "Session ID: $SESSION_ID"
echo "Timestamp: $(date)"
echo ""

# Helper functions
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_service() {
    local url=$1
    local service_name=${2:-"Unknown"}
    
    log_info "Checking $service_name..."
    
    if curl -s --connect-timeout 5 "$url/healthz" > /dev/null; then
        log_success "$service_name is running and healthy"
        return 0
    else
        log_error "$service_name is not responding (expected URL: $url)"
        return 1
    fi
}

get_json_field() {
    local json_response="$1"
    local field="$2"
    echo "$json_response" | jq -r ".$field // empty"
}

test_mod1_health() {
    log_info "Testing Mod1_v2 (ASR) Health Check"
    
    local response=$(curl -s --connect-timeout 5 "$MOD1_URL/healthz")
    local status=$(get_json_field "$response" "status")
    local asr_status=$(get_json_field "$response" "asr")
    
    if [[ "$status" == "ok" && "$asr_status" == "ready" ]]; then
        log_success "Mod1_v2 health check passed"
        echo "  Status: $status"
        echo "  ASR: $asr_status"
        echo "  Service: $(get_json_field "$response" "service")"
        return 0
    else
        log_error "Mod1_v2 health check failed"
        echo "  Response: $response"
        return 1
    fi
}

test_mod2_health() {
    log_info "Testing Mod2-v1 (NLP) Health Check"
    
    local response=$(curl -s --connect-timeout 5 "$MOD2_URL/healthz")
    local status=$(get_json_field "$response" "status")
    local layout_provider=$(get_json_field "$response" "layout_provider")
    
    if [[ "$status" == "ok" ]]; then
        log_success "Mod2-v1 health check passed"
        echo "  Status: $status"
        echo "  Layout Provider: $layout_provider"
        echo "  Mod3 URL: $(get_json_field "$response" "mod3_url")"
        echo "  NLP Debug: $(get_json_field "$response" "nlp_debug")"
        return 0
    else
        log_error "Mod2-v1 health check failed"
        echo "  Response: $response"
        return 1
    fi
}

test_mod3_health() {
    log_info "Testing Mod3-v1 (Visual Mapping) Health Check"
    
    local response=$(curl -s --connect-timeout 5 "$MOD3_URL/healthz")
    local status=$(get_json_field "$response" "status")
    
    if [[ "$status" == "ok" ]]; then
        log_success "Mod3-v1 health check passed"
        echo "  Status: $status"
        echo "  Database: $(get_json_field "$response" "database_url")"
        
        # Check feature flags
        local require_props=$(get_json_field "$response" "feature_flags.require_props")
        local names_normalize=$(get_json_field "$response" "feature_flags.names_normalize")
        local max_matches=$(get_json_field "$response" "feature_flags.max_matches")
        
        echo "  Feature Flags:"
        echo "    Require Props: $require_props"
        echo "    Names Normalize: $names_normalize"
        echo "    Max Matches: $max_matches"
        return 0
    else
        log_error "Mod3-v1 health check failed"
        echo "  Response: $response"
        return 1
    fi
}

test_mod2_text_processing() {
    log_info "Testing Mod2-v1 Text Processing"
    
    local test_text="Сделай сайт с заголовком и кнопкой отправки формы"
    
    local response=$(curl -s --connect-timeout 10 -X POST "$MOD2_URL/v2/ingest/chunk" \
        -H "Content-Type: application/json" \
        -d "{
            \"session_id\": \"$SESSION_ID\",
            \"chunk_id\": \"chunk_001\", 
            \"seq\": 1,
            \"text\": \"$test_text\",
            \"lang\": \"ru-RU\",
            \"timestamp\": $(date +%s000)
        }")
    
    local status=$(get_json_field "$response" "status")
    
    if [[ "$status" == "ok" ]]; then
        log_success "Mod2-v1 text processing passed"
        echo "  Session ID: $(get_json_field "$response" "session_id")"
        echo "  Chunk ID: $(get_json_field "$response" "chunk_id")"
        echo "  Text Length: ${#test_text} characters"
        return 0
    else
        log_error "Mod2-v1 text processing failed"
        echo "  Response: $response"
        return 1
    fi
}

test_mod2_entities_extraction() {
    log_info "Testing Mod2-v1 Entities Extraction"
    
    # Wait a moment for processing to complete
    sleep 2
    
    local response=$(curl -s --connect-timeout 5 -X GET "$MOD2_URL/v2/session/$SESSION_ID/entities")
    local status=$(get_json_field "$response" "status")
    local entities_count=$(echo "$response" | jq -r '.entities | length')
    local keyphrases_count=$(echo "$response" | jq -r '.keyphrases | length')
    
    if [[ "$status" == "ok" && "$entities_count" -gt 0 ]]; then
        log_success "Mod2-v1 entities extraction passed"
        echo "  Entity Count: $entities_count"
        echo "  Keyphrase Count: $keyphrases_count"
        echo "  Chunks Processed: $(get_json_field "$response" "chunks_processed")"
        
        # Show extracted entities
        local entities=$(echo "$response" | jq -r '.entities[]' | tr '\n' ', ' | sed 's/,$//')
        echo "  Extracted Entities: $entities"
        return 0
    else
        log_error "Mod2-v1 entities extraction failed"
        echo "  Response: $response"
        return 1
    fi
}

test_mod3_component_catalog() {
    log_info "Testing Mod3-v1 Component Catalog"
    
    local response=$(curl -s --connect-timeout 5 -X GET "$MOD3_URL/v1/components")
    local status=$(get_json_field "$response" "status")
    local components_count=$(echo "$response" | jq -r '.components | length')
    
    if [[ "$status" == "ok" && "$components_count" -gt 0 ]]; then
        log_success "Mod3-v1 component catalog passed"
        echo "  Components Available: $components_count"
        
        # Check for key components
        local ui_hero=$(echo "$response" | jq -r '.components[] | select(.name=="ui.hero") | .name // empty')
        local ui_button=$(echo "$response" | jq -r '.components[] | select(.name=="ui.button") | .name // empty')
        local ui_heading=$(echo "$response" | jq -r '.components[] | select(.name=="ui.heading") | .name // empty')
        
        echo "  Key Components:"
        [[ -n "$ui_hero" ]] && echo "    ✅ ui.hero found" || echo "    ❌ ui.hero missing"
        [[ -n "$ui_button" ]] && echo "    ✅ ui.button found" || echo "    ❌ ui.button missing"
        [[ -n "$ui_heading" ]] && echo "    ✅ ui.heading found" || echo "    ❌ ui.heading missing"
        
        return 0
    else
        log_error "Mod3-v1 component catalog failed"
        echo "  Response: $response"
        return 1
    fi
}

test_mod3_layout_generation() {
    log_info "Testing Mod3-v1 Layout Generation"
    
    local test_entities='["заголовок", "кнопка", "форма"]'
    local test_keyphrases='["кнопка отправки формы"]'
    
    local response=$(curl -s --connect-timeout 10 -X POST "$MOD3_URL/v1/map" \
        -H "Content-Type: application/json" \
        -d "{
            \"session_id\": \"$SESSION_ID\",
            \"entities\": $test_entities,
            \"keyphrases\": $test_keyphrases,
            \"template\": \"hero-main-footer\"
        }")
    
    local status=$(get_json_field "$response" "status")
    local layout_count=$(get_json_field "$response" "layout.count")
    local hero_count=$(echo "$response" | jq -r '.layout.sections.hero | length')
    local main_count=$(echo "$response" | jq -r '.layout.sections.main | length')
    local footer_count=$(echo "$response" | jq -r '.layout.sections.footer | length')
    
    if [[ "$status" == "ok" && "$layout_count" -gt 0 ]]; then
        log_success "Mod3-v1 layout generation passed"
        echo "  Total Components: $layout_count"
        echo "  Hero Components: $hero_count"
        echo "  Main Components: $main_count"
        echo "  Footer Components: $footer_count"
        echo "  Template: $(get_json_field "$response" "layout.template")"
        
        # Check component props
        local components_without_props=0
        local components_with_ui_prefix=0
        
        # Validate main section components
        echo "$response" | jq -r '.layout.sections.main[]? | {component, props}' | while read -r main_component; do
            local component_name=$(echo "$main_component" | jq -r '.component // empty')
            if [[ -n "$component_name" ]]; then
                if [[ "$component_name" =~ ^ui\. ]]; then
                    components_with_ui_prefix=$((components_with_ui_prefix + 1))
                fi
            fi
        done
        
        echo "  Components with 'ui.' prefix: $components_with_ui_prefix"
        
        # Show explanations
        local explanations_count=$(echo "$response" | jq -r '.explanations | length')
        echo "  Explanations Count: $explanations_count"
        
        return 0
    else
        log_error "Mod3-v1 layout generation failed"
        echo "  Response: $response"
        return 1
    fi
}

test_integration_flow() {
    log_info "Testing Complete Integration Flow"
    
    local integration_text="Создайте красивую страницу с меню навигации и формой обратной связи"
    local integration_session="integration_$(date +%s)"
    
    # Step 1: Send text to Mod2
    local ingest_response=$(curl -s --connect-timeout 10 -X POST "$MOD2_URL/v2/ingest/chunk" \
        -H "Content-Type: application/json" \
        -d "{
            \"session_id\": \"$integration_session\",
            \"chunk_id\": \"chunk_int\", 
            \"seq\": 1,
            \"text\": \"$integration_text\",
            \"lang\": \"ru-RU\",
            \"timestamp\": $(date +%s000)
        }")
    
    # Wait for processing
    sleep 3
    
    # Step 2: Get entities from Mod2
    local entities_response=$(curl -s --connect-timeout 5 -X GET "$MOD2_URL/v2/session/$integration_session/entities")
    local entities_json=$(echo "$entities_response" | jq -r '.entities')
    local keyphrases_json=$(echo "$entities_response" | jq -r '.keyphrases')
    
    # Step 3: Send to Mod3
    local layout_response=$(curl -s --connect-timeout 10 -X POST "$MOD3_URL/v1/map" \
        -H "Content-Type: application/json" \
        -d "{
            \"session_id\": \"$integration_session\",
            \"entities\": $entities_json,
            \"keyphrases\": $keyphrases_json,
            \"template\": \"hero-main-footer\"
        }")
    
    local final_status=$(get_json_field "$layout_response" "status")
    local final_count=$(get_json_field "$layout_response" "layout.count")
    
    if [[ "$final_status" == "ok" && "$final_count" -gt 0 ]]; then
        log_success "Complete integration flow passed"
        echo "  Session: $integration_session"
        echo "  Input Text: $integration_text"
        echo "  Final Layout Components: $final_count"
        echo "  Mod3 Template: $(get_json_field "$layout_response" "layout.template")"
        return 0
    else
        log_error "Complete integration flow failed"
        echo "  Ingest Status: $(get_json_field "$ingest_response" "status")"
        echo "  Entities Status: $(get_json_field "$entities_response" "status")"
        echo "  Layout Status: $final_status"
        return 1
    fi
}

# Main test execution
main() {
    local test_results=()
    local total_tests=0
    
    # Initialize test counter
    total_tests=8
    
    echo -e "${BLUE}Phase 1: Health Checks${NC}"
    echo "======================="
    
    if test_mod1_health; then
        test_results+=(0)
    else
        test_results+=(1)
    fi
    
    if test_mod2_health; then
        test_results+=(0)
    else
        test_results+=(1)
    fi
    
    if test_mod3_health; then
        test_results+=(0)
    else
        test_results+=(1)
    fi
    
    echo ""
    echo -e "${BLUE}Phase 2: Individual Module Tests${NC}"
    echo "===================================="
    
    if test_mod2_text_processing; then
        test_results+=(0)
    else
        test_results+=(1)
    fi
    
    if test_mod2_entities_extraction; then
        test_results+=(0)
    else
        test_results+=(1)
    fi
    
    if test_mod3_component_catalog; then
        test_results+=(0)
    else
        test_results+=(1)
    fi
    
    if test_mod3_layout_generation; then
        test_results+=(0)
    else
        test_results+=(1)
    fi
    
    echo ""
    echo -e "${BLUE}Phase 3: Integration Testing${NC}"
    echo "============================="
    
    if test_integration_flow; then
        test_results+=(0)
    else
        test_results+=(1)
    fi
    
    # Calculate results
    local passed_tests=0
    for result in "${test_results[@]}"; do
        if [[ $result -eq 0 ]]; then
            ((passed_tests++))
        fi
    done
    
    echo ""
    echo -e "${BLUE}Test Summary${NC}"
    echo "============="
    echo "Total Tests: $total_tests"
    echo -e "Passed: ${GREEN}$passed_tests${NC}"
    echo -e "Failed: ${RED}$((total_tests - passed_tests))${NC}"
    
    # Success criteria
    if [[ $passed_tests -ge 6 ]]; then
        echo ""
        log_success "All smoke tests passed! System is ready for use."
        echo ""
        echo -e "${GREEN}✅ SUCCESS CRITERIA MET:${NC}"
        echo "  - All health checks respond"
        echo "  - Mod2 processes text and extracts entities"
        echo "  - Mod3 returns valid layouts with components > 0"
        echo "  - End-to-end integration flow works"
        echo "  - All modules communicate correctly"
        exit 0
    else
        echo ""
        log_error "Some tests failed. Please check the issues above."
        echo ""
        echo -e "${RED}❌ COMMON FIXES:${NC}"
        echo "  1. Ensure all modules are running on correct ports"
        echo "  2. Check .env files are present in each module"
        echo "  3. Verify database initialization (run init scripts)"
        echo "  4. Check logs for detailed error information"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    local missing_deps=()
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install: sudo apt-get install curl jq"
        exit 1
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_dependencies
    main "$@"
fi
