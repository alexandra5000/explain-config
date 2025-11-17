"""Documentation manager for Elastic EDOT Collector docs."""

import os
import sys
import zipfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import requests


class DocsManager:
    """Manage downloading, caching, and retrieving Elastic and upstream OpenTelemetry documentation."""
    
    DOCS_URL = "https://www.elastic.co/docs/llm.zip"
    OTEL_COLLECTOR_REPO = "https://github.com/open-telemetry/opentelemetry-collector-contrib"
    OTEL_COLLECTOR_DOCS_URL = "https://api.github.com/repos/open-telemetry/opentelemetry-collector-contrib/contents"
    CACHE_DIR = Path.home() / ".explain_config" / "elastic_docs"
    OTEL_CACHE_DIR = Path.home() / ".explain_config" / "otel_docs"
    CACHE_INFO_FILE = CACHE_DIR / "cache_info.json"
    OTEL_CACHE_INFO_FILE = OTEL_CACHE_DIR / "cache_info.json"
    CACHE_EXPIRY_DAYS = 7
    
    def __init__(self, cache_dir: Optional[Path] = None, include_upstream: bool = True):
        """
        Initialize docs manager.
        
        Args:
            cache_dir: Optional custom cache directory (default: ~/.explain_config/elastic_docs)
            include_upstream: Whether to include upstream OpenTelemetry Collector docs (default: True)
        """
        if cache_dir:
            self.CACHE_DIR = Path(cache_dir)
            self.CACHE_INFO_FILE = self.CACHE_DIR / "cache_info.json"
        
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.extracted_dir = self.CACHE_DIR / "extracted"
        
        self.include_upstream = include_upstream
        self.OTEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.otel_docs_dir = self.OTEL_CACHE_DIR / "collector_docs"
    
    def _get_cache_info(self) -> Dict:
        """Get cache metadata."""
        if self.CACHE_INFO_FILE.exists():
            try:
                with open(self.CACHE_INFO_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_cache_info(self, info: Dict):
        """Save cache metadata."""
        with open(self.CACHE_INFO_FILE, 'w') as f:
            json.dump(info, f)
    
    def _is_cache_stale(self) -> bool:
        """Check if cached docs are stale."""
        cache_info = self._get_cache_info()
        if not cache_info.get("last_updated"):
            return True
        
        try:
            last_updated = datetime.fromisoformat(cache_info["last_updated"])
            expiry_date = last_updated + timedelta(days=self.CACHE_EXPIRY_DAYS)
            return datetime.now() > expiry_date
        except (ValueError, KeyError):
            return True
    
    def download_docs(self, force: bool = False) -> bool:
        """
        Download and extract Elastic docs.
        
        Args:
            force: Force download even if cache is fresh
            
        Returns:
            True if docs were downloaded/extracted, False if using existing cache
        """
        if not force and not self._is_cache_stale() and self.extracted_dir.exists():
            return False
        
        print("Downloading Elastic documentation...", file=sys.stderr)
        
        try:
            # Download zip
            response = requests.get(self.DOCS_URL, timeout=30)
            response.raise_for_status()
            
            zip_path = self.CACHE_DIR / "docs.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extract zip
            if self.extracted_dir.exists():
                import shutil
                shutil.rmtree(self.extracted_dir)
            self.extracted_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.extracted_dir)
            
            # Save cache info
            self._save_cache_info({
                "last_updated": datetime.now().isoformat(),
                "version": "unknown"  # Could parse from zip if available
            })
            
            print("Documentation downloaded and cached.", file=sys.stderr)
            return True
            
        except requests.RequestException as e:
            raise Exception(f"Failed to download docs: {e}")
        except zipfile.BadZipFile:
            raise Exception("Downloaded file is not a valid zip archive")
        except Exception as e:
            raise Exception(f"Error processing docs: {e}")
    
    def _get_otel_cache_info(self) -> Dict:
        """Get OpenTelemetry docs cache metadata."""
        if self.OTEL_CACHE_INFO_FILE.exists():
            try:
                with open(self.OTEL_CACHE_INFO_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_otel_cache_info(self, info: Dict):
        """Save OpenTelemetry docs cache metadata."""
        with open(self.OTEL_CACHE_INFO_FILE, 'w') as f:
            json.dump(info, f)
    
    def _is_otel_cache_stale(self) -> bool:
        """Check if cached OpenTelemetry docs are stale."""
        cache_info = self._get_otel_cache_info()
        if not cache_info.get("last_updated"):
            return True
        
        try:
            last_updated = datetime.fromisoformat(cache_info["last_updated"])
            expiry_date = last_updated + timedelta(days=self.CACHE_EXPIRY_DAYS)
            return datetime.now() > expiry_date
        except (ValueError, KeyError):
            return True
    
    def download_otel_docs(self, force: bool = False) -> bool:
        """
        Download upstream OpenTelemetry Collector documentation from GitHub.
        
        Args:
            force: Force download even if cache is fresh
            
        Returns:
            True if docs were downloaded, False if using existing cache
        """
        if not self.include_upstream:
            return False
            
        if not force and not self._is_otel_cache_stale() and self.otel_docs_dir.exists():
            return False
        
        print("Downloading upstream OpenTelemetry Collector documentation...", file=sys.stderr)
        
        try:
            # Use GitHub API to get docs directory contents
            import time
            
            # Component directories in the contrib repo
            component_types = ["receiver", "processor", "exporter", "extension"]
            
            if self.otel_docs_dir.exists():
                import shutil
                shutil.rmtree(self.otel_docs_dir)
            self.otel_docs_dir.mkdir(parents=True, exist_ok=True)
            
            # Fetch README files from component directories
            # Use raw.githubusercontent.com directly to avoid API rate limits entirely
            files_downloaded = 0
            
            # Common component names - we'll try these directly via raw URLs
            # This avoids the API rate limit issue completely
            common_components = {
                "receiver": [
                    "otlpreceiver", "prometheusreceiver", "jaegerreceiver", "zipkinreceiver",
                    "filelogreceiver", "syslogreceiver", "fluentforwardreceiver", "kafkareceiver",
                    "redisreceiver", "postgresqlreceiver", "mysqlreceiver", "mongodbreceiver",
                    "elasticsearchreceiver", "apachereceiver", "nginxreceiver", "hostmetricsreceiver",
                    "kubeletstatsreceiver", "k8sclusterreceiver", "k8seventsreceiver", "k8sobjectsreceiver",
                    "dockerstatsreceiver", "statsdreceiver", "carbonreceiver", "collectdreceiver",
                    "jmxreceiver", "sapmreceiver", "splunkhecreceiver", "wavefrontreceiver",
                    "signalfxreceiver", "datadogreceiver", "awsxrayreceiver", "awsecscontainermetricsreceiver",
                    "awscloudwatchmetricsreceiver", "azuremonitorreceiver", "googlecloudspannerreceiver",
                    "googlecloudpubsubreceiver", "azureeventhubreceiver", "snowflakereceiver"
                ],
                "processor": [
                    "batchprocessor", "memorylimiterprocessor", "probabilisticsamplerprocessor",
                    "attributesprocessor", "resourceprocessor", "transformprocessor", "filterprocessor",
                    "spanprocessor", "metricstransformprocessor", "routingprocessor", "groupbytraceprocessor",
                    "cumulativetodeltaprocessor", "deltatorateprocessor", "tail_samplingprocessor",
                    "servicegraphprocessor", "spanmetricsprocessor", "k8sattributesprocessor",
                    "resourcedetectionprocessor", "redactionprocessor", "groupbyattrsprocessor"
                ],
                "exporter": [
                    "otlpexporter", "otlphttpexporter", "prometheusexporter", "prometheusremotewriteexporter",
                    "jaegerexporter", "zipkinexporter", "kafkaexporter", "fileexporter", "loggingexporter",
                    "elasticsearchexporter", "splunkhecexporter", "signalfxexporter", "datadogexporter",
                    "awsxrayexporter", "awscloudwatchlogsexporter", "awscloudwatchmetricsexporter",
                    "googlecloudpubsubexporter", "googlecloudstorageexporter", "azuremonitorexporter",
                    "azureeventhubrexporter", "sapmexporter", "wavefrontexporter", "carbonexporter",
                    "collectdexporter", "influxdbexporter", "sentryexporter", "newrelicexporter"
                ],
                "extension": [
                    "healthcheckextension", "pprofextension", "zpagesextension", "bearertokenauthextension",
                    "oauth2clientauthextension", "oidcauthextension", "basicauthextension",
                    "awsauthextension", "headerssetterextension", "filestorageextension",
                    "memoryballastextension", "k8sobserverextension", "hostobserverextension"
                ]
            }
            
            for component_type in component_types:
                # Create subdirectory for this component type
                type_dir = self.otel_docs_dir / component_type
                type_dir.mkdir(parents=True, exist_ok=True)
                
                # Try to get full list via API first (if not rate limited)
                components_to_try = []
                api_url = f"https://api.github.com/repos/open-telemetry/opentelemetry-collector-contrib/contents/{component_type}"
                try:
                    response = requests.get(api_url, timeout=30)
                    if response.status_code == 200:
                        components = response.json()
                        if isinstance(components, list):
                            components_to_try = [c.get("name", "") for c in components if c.get("type") == "dir" and c.get("name")]
                            print(f"Found {len(components_to_try)} {component_type} components via API, downloading...", file=sys.stderr)
                except Exception:
                    pass
                
                # Fallback to common components if API fails
                if not components_to_try:
                    components_to_try = common_components.get(component_type, [])
                    print(f"Using {len(components_to_try)} common {component_type} components, downloading...", file=sys.stderr)
                
                # Download README.md from each component using raw URLs (no API rate limits)
                for component_name in components_to_try:
                    if not component_name:
                        continue
                    
                    try:
                        # Use raw.githubusercontent.com directly (no API rate limits for raw content)
                        # This is much faster and doesn't count against API rate limits
                        raw_url = f"https://raw.githubusercontent.com/open-telemetry/opentelemetry-collector-contrib/main/{component_type}/{component_name}/README.md"
                        file_response = requests.get(raw_url, timeout=30)
                        
                        if file_response.status_code == 200:
                            file_path = type_dir / f"{component_name}.md"
                            try:
                                file_path.write_text(file_response.text, encoding='utf-8')
                                files_downloaded += 1
                                if files_downloaded % 20 == 0:
                                    print(f"Downloaded {files_downloaded} files...", file=sys.stderr)
                            except (IOError, OSError) as e:
                                # Handle broken pipe or file write errors gracefully
                                print(f"Warning: Could not write {file_path}: {e}", file=sys.stderr)
                                continue
                        elif file_response.status_code == 404:
                            # Component doesn't have README, skip silently
                            continue
                        elif file_response.status_code == 403:
                            # Rate limited - add delay and continue
                            print(f"Rate limited, waiting 2 seconds...", file=sys.stderr)
                            time.sleep(2)
                            continue
                        else:
                            # Other error, skip this component
                            continue
                        
                        # Small delay to be respectful
                        time.sleep(0.05)
                        
                    except requests.exceptions.RequestException as e:
                        # Handle network errors gracefully
                        continue
                    except (IOError, OSError) as e:
                        # Handle broken pipe and other I/O errors
                        continue
                    except Exception as e:
                        # Skip components without README or with other errors
                        continue
            
            if files_downloaded > 0:
                self._save_otel_cache_info({
                    "last_updated": datetime.now().isoformat(),
                    "files_downloaded": files_downloaded
                })
                print(f"Downloaded {files_downloaded} OpenTelemetry documentation files.", file=sys.stderr)
                return True
            else:
                print("Warning: No OpenTelemetry docs were downloaded.", file=sys.stderr)
                return False
                
        except requests.RequestException as e:
            raise Exception(f"Failed to download OpenTelemetry docs: {e}")
        except Exception as e:
            raise Exception(f"Error processing OpenTelemetry docs: {e}")
    
    def get_edot_collector_docs(self) -> List[str]:
        """
        Get relevant EDOT collector documentation content.
        
        Returns:
            List of documentation file paths/content
        """
        if not self.extracted_dir.exists():
            return []
        
        docs = []
        
        # Find EDOT collector reference docs
        edot_ref_dir = self.extracted_dir / "reference" / "edot-collector"
        if edot_ref_dir.exists():
            # Get main reference doc
            main_doc = edot_ref_dir / "edot-collector.md"
            if main_doc.exists():
                docs.append(str(main_doc))
            
            # Get config documentation
            config_dir = edot_ref_dir / "config"
            if config_dir.exists():
                for config_file in config_dir.rglob("*.md"):
                    docs.append(str(config_file))
            
            # Get components documentation
            components_dir = edot_ref_dir / "components"
            if components_dir.exists():
                for component_file in components_dir.rglob("*.md"):
                    docs.append(str(component_file))
        
        # Also get general OpenTelemetry reference
        otel_ref = self.extracted_dir / "reference" / "opentelemetry"
        if otel_ref.exists():
            for otel_file in otel_ref.rglob("*.md"):
                if "edot" in str(otel_file).lower() or "collector" in str(otel_file).lower():
                    docs.append(str(otel_file))
        
        return docs
    
    def get_otel_collector_docs(self) -> List[str]:
        """
        Get upstream OpenTelemetry Collector documentation files.
        
        Returns:
            List of documentation file paths
        """
        if not self.include_upstream or not self.otel_docs_dir.exists():
            return []
        
        docs = []
        
        # Get all markdown files from the downloaded OTel docs
        for md_file in self.otel_docs_dir.rglob("*.md"):
            docs.append(str(md_file))
        
        return docs
    
    def get_component_context(self, component_type: str, component_name: str, 
                             component_config: Optional[Dict] = None) -> str:
        """
        Get relevant documentation context for a specific component.
        
        Args:
            component_type: Type of component (receiver, processor, exporter, etc.)
            component_name: Name of the component
            component_config: Optional component configuration dict for field-specific context
            
        Returns:
            Relevant documentation context as string
        """
        docs = self.get_edot_collector_docs()
        
        # Also get upstream OpenTelemetry docs if available
        if self.include_upstream:
            otel_docs = self.get_otel_collector_docs()
            docs.extend(otel_docs)
        
        context_parts = []
        
        # Try to find component-specific docs
        component_lower = component_name.lower()
        component_type_lower = component_type.lower()
        
        # Priority 1: Look for exact component name in file path
        exact_matches = []
        # Priority 2: Look for component name in content
        content_matches = []
        # Priority 3: General component type docs
        type_matches = []
        
        for doc_path in docs:
            try:
                doc_file = Path(doc_path)
                if not doc_file.exists():
                    continue
                
                # Check filename first (most specific)
                filename_lower = doc_file.name.lower()
                if component_lower in filename_lower or component_name in filename_lower:
                    exact_matches.append(doc_file)
                    continue
                
                # Read doc content
                content = doc_file.read_text(encoding='utf-8', errors='ignore')
                content_lower = content.lower()
                
                # Check for component name in content (with word boundaries for better matching)
                if (f"{component_lower}" in content_lower or 
                    f"{component_name}" in content):
                    content_matches.append((doc_file, content))
                elif component_type_lower in content_lower:
                    type_matches.append((doc_file, content))
                    
            except Exception:
                continue
        
        # Process exact matches first (most relevant)
        for doc_file in exact_matches[:2]:  # Limit to 2 files
            try:
                content = doc_file.read_text(encoding='utf-8', errors='ignore')
                # Extract more content for exact matches (3000 chars)
                context_parts.append(f"---\nFrom: {doc_file.name}\n{content[:3000]}\n---")
            except Exception:
                continue
        
        # Process content matches
        for doc_file, content in content_matches[:2]:
            # Extract relevant section around component mentions
            sections = self._extract_relevant_sections(content, component_name, component_config)
            if sections:
                context_parts.append(f"---\nFrom: {doc_file.name}\n{sections}\n---")
            else:
                # Fallback to first 2000 chars
                context_parts.append(f"---\nFrom: {doc_file.name}\n{content[:2000]}\n---")
        
        # If we have field-specific config, try to find field documentation
        if component_config and len(context_parts) < 3:
            field_context = self._get_field_context(component_name, component_config)
            if field_context:
                context_parts.append(f"---\nField-specific context:\n{field_context}\n---")
        
        # Add troubleshooting context if available
        troubleshooting_context = self._get_troubleshooting_context(component_name)
        if troubleshooting_context and len(context_parts) < 3:
            context_parts.append(f"---\nTroubleshooting:\n{troubleshooting_context}\n---")
        
        # If no specific docs found, include general EDOT collector reference
        if not context_parts:
            edot_ref = self.extracted_dir / "reference" / "edot-collector" / "edot-collector.md"
            if edot_ref.exists():
                try:
                    content = edot_ref.read_text(encoding='utf-8', errors='ignore')
                    context_parts.append(f"---\nFrom: EDOT Collector Reference\n{content[:2000]}\n---")
                except Exception:
                    pass
        
        return "\n\n".join(context_parts[:3])  # Limit to 3 context blocks
    
    def _extract_relevant_sections(self, content: str, component_name: str, 
                                   component_config: Optional[Dict] = None) -> str:
        """Extract relevant sections from documentation that mention the component."""
        lines = content.split('\n')
        relevant_lines = []
        in_relevant_section = False
        section_start = None
        
        component_lower = component_name.lower()
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if this line mentions the component
            if component_lower in line_lower or component_name in line:
                # Start capturing from a few lines before
                section_start = max(0, i - 3)
                in_relevant_section = True
            
            # If we're in a relevant section, capture lines
            if in_relevant_section:
                relevant_lines.append(line)
                
                # Stop after capturing a reasonable chunk (50 lines or ~2000 chars)
                if len(relevant_lines) > 50 or len('\n'.join(relevant_lines)) > 2000:
                    break
                
                # Stop if we hit a new major section (heading)
                if line.startswith('#') and i > section_start + 10:
                    break
        
        result = '\n'.join(relevant_lines)
        return result if len(result) > 100 else ""  # Only return if substantial
    
    def _get_field_context(self, component_name: str, component_config: Dict) -> str:
        """Get context about specific fields in the component configuration."""
        # Look for configuration examples or field documentation
        config_dir = self.extracted_dir / "reference" / "edot-collector" / "config"
        if not config_dir.exists():
            return ""
        
        field_info = []
        component_lower = component_name.lower()
        
        # Get all config keys from the component
        config_keys = list(component_config.keys()) if isinstance(component_config, dict) else []
        
        for config_file in config_dir.rglob("*.md"):
            try:
                content = config_file.read_text(encoding='utf-8', errors='ignore')
                content_lower = content.lower()
                
                # Check if this file mentions the component
                if component_lower in content_lower:
                    # Look for YAML examples or field descriptions
                    # Extract code blocks that might contain config examples
                    import re
                    code_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
                    for block in code_blocks[:2]:  # Limit to 2 examples
                        if component_lower in block.lower():
                            field_info.append(f"Example configuration:\n{block[:1000]}")
                            break
            except Exception:
                continue
        
        return "\n\n".join(field_info[:2])  # Limit to 2 field contexts
    
    def _get_troubleshooting_context(self, component_name: str) -> str:
        """Get troubleshooting information for a component."""
        troubleshoot_dir = self.extracted_dir / "troubleshoot" / "ingest" / "opentelemetry"
        if not troubleshoot_dir.exists():
            return ""
        
        component_lower = component_name.lower()
        troubleshooting_info = []
        
        # Look for component-specific troubleshooting
        for troubleshoot_file in troubleshoot_dir.rglob("*.md"):
            try:
                filename_lower = troubleshoot_file.name.lower()
                if component_lower in filename_lower:
                    content = troubleshoot_file.read_text(encoding='utf-8', errors='ignore')
                    # Extract first 1500 chars of troubleshooting info
                    troubleshooting_info.append(f"From: {troubleshoot_file.name}\n{content[:1500]}")
                    break
            except Exception:
                continue
        
        # Also check general troubleshooting
        general_troubleshoot = troubleshoot_dir / "opentelemetry.md"
        if general_troubleshoot.exists() and not troubleshooting_info:
            try:
                content = general_troubleshoot.read_text(encoding='utf-8', errors='ignore')
                if component_lower in content.lower():
                    troubleshooting_info.append(f"From: General OpenTelemetry Troubleshooting\n{content[:1500]}")
            except Exception:
                pass
        
        return "\n\n".join(troubleshooting_info[:1])  # Limit to 1 troubleshooting doc
    
    def get_cache_status(self) -> Dict:
        """Get information about cached docs."""
        cache_info = self._get_cache_info()
        otel_cache_info = self._get_otel_cache_info() if self.include_upstream else {}
        
        status = {
            "cached": self.extracted_dir.exists(),
            "stale": self._is_cache_stale(),
            "last_updated": cache_info.get("last_updated", "Never"),
            "cache_dir": str(self.CACHE_DIR),
            "upstream_enabled": self.include_upstream
        }
        
        if self.include_upstream:
            status["otel_cached"] = self.otel_docs_dir.exists()
            status["otel_stale"] = self._is_otel_cache_stale()
            status["otel_last_updated"] = otel_cache_info.get("last_updated", "Never")
            status["otel_files"] = otel_cache_info.get("files_downloaded", 0)
            status["otel_cache_dir"] = str(self.OTEL_CACHE_DIR)
        
        return status

