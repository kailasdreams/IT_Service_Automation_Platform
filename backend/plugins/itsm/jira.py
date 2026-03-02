"""Jira Service Management plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.itsm.base import BaseITSMPlugin
from backend.plugins.base import PluginResult
import base64


class JiraPlugin(BaseITSMPlugin):
    """Jira Service Management connector."""
    
    version = "1.0.0"
    description = "Jira Service Management connector - REST API v3, Webhooks integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["api_url", "username", "api_token"]
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Jira uses basic auth with API token."""
        username = self.config.get("username", "")
        api_token = self.config.get("api_token", "")
        credentials = base64.b64encode(f"{username}:{api_token}".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }
    
    async def create_ticket(self, title: str, description: str, priority: str = "medium", **kwargs) -> PluginResult:
        """Create issue in Jira."""
        try:
            url = "/rest/api/3/issue"
            priority_map = {
                "critical": "Highest",
                "high": "High",
                "medium": "Medium",
                "low": "Low",
            }
            project_key = kwargs.get("project_key", self.config.get("project_key", "IT"))
            issue_type = kwargs.get("issue_type", "Incident")
            
            data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": title,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": description}],
                            }
                        ],
                    },
                    "issuetype": {"name": issue_type},
                    "priority": {"name": priority_map.get(priority.lower(), "Medium")},
                    **kwargs.get("fields", {}),
                }
            }
            response = await self.client.post(url, json=data)
            
            if response.status_code in [200, 201]:
                issue = response.json()
                return PluginResult(
                    success=True,
                    data={
                        "ticket_id": issue.get("id"),
                        "key": issue.get("key"),
                        "ticket": issue,
                    }
                )
            return PluginResult(success=False, error=f"API error: {response.status_code} - {response.text}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def update_ticket(self, ticket_id: str, **kwargs) -> PluginResult:
        """Update Jira issue."""
        try:
            url = f"/rest/api/3/issue/{ticket_id}"
            # Convert kwargs to Jira fields format
            fields = {}
            if "title" in kwargs:
                fields["summary"] = kwargs.pop("title")
            if "description" in kwargs:
                fields["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": kwargs.pop("description")}]}],
                }
            fields.update(kwargs.get("fields", {}))
            
            data = {"fields": fields} if fields else kwargs
            response = await self.client.put(url, json=data)
            
            if response.status_code == 204:
                return PluginResult(success=True, data={"message": "Issue updated"})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def get_ticket(self, ticket_id: str) -> PluginResult:
        """Get Jira issue."""
        try:
            url = f"/rest/api/3/issue/{ticket_id}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                issue = response.json()
                return PluginResult(success=True, data={"ticket": issue})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def search_tickets(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Search Jira issues using JQL."""
        try:
            url = "/rest/api/3/search"
            jql = filters.get("jql", "") if filters else ""
            params = {"jql": jql, "maxResults": filters.get("maxResults", 50)} if filters else {}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                results = response.json()
                issues = results.get("issues", [])
                return PluginResult(success=True, data={"tickets": issues, "total": results.get("total", 0)})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
