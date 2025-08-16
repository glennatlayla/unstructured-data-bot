# User Guide

## Overview
This guide covers end-user documentation for the Unstructured Data Indexing & AI-Query Application, including Teams bot usage and admin interface operations.

## Teams Bot Usage

### Getting Started
1. **Install the Bot**: Add the bot to your Teams workspace
2. **Connect Data Sources**: Link your Box and Microsoft 365 accounts
3. **Start Querying**: Ask questions about your documents

### Basic Commands
```
# Ask questions about documents
"What documents contain budget information?"

# Search for specific content
"Find documents mentioning Q4 2024"

# Get document summaries
"Summarize the quarterly report"

# List available documents
"What documents do I have access to?"
```

### Advanced Queries
```
# Multi-document analysis
"Compare the budget across all departments"

# Time-based queries
"What changed in our policies since January?"

# Content analysis
"Which documents contain sensitive information?"

# Cross-reference queries
"Find documents that reference both project A and budget B"
```

### Bot Responses
- **Direct Answers**: Clear, concise responses with citations
- **Tables**: Structured data in easy-to-read format
- **Charts**: Visual representations when appropriate
- **Citations**: Links to source documents
- **Follow-up**: Suggested related questions

## Admin Interface

### Access and Authentication
1. **Login**: Use your Microsoft 365 credentials
2. **Role Assignment**: Contact your administrator for permissions
3. **Multi-factor Authentication**: Required for admin access

### Dashboard Overview
- **System Health**: Service status and performance metrics
- **Usage Statistics**: Query volume and user activity
- **Cost Tracking**: Azure resource usage and forecasting
- **Recent Activity**: Latest queries and system events

### Policy Management

#### Sensitive Data Policies
```json
{
  "policy_name": "Financial Data Protection",
  "categories": ["PII", "PCI", "Trade Secrets"],
  "detectors": {
    "credit_card": true,
    "ssn": true,
    "account_numbers": true
  },
  "behaviors": {
    "pii": "mask",
    "pci": "block",
    "trade_secrets": "alert"
  }
}
```

#### Policy Configuration
1. **Create Policy**: Define new sensitive data categories
2. **Configure Detectors**: Enable/disable built-in patterns
3. **Set Behaviors**: Choose how to handle sensitive data
4. **Test Policies**: Validate with sample content
5. **Deploy**: Apply policies across the system

### Directory Management

#### Source Configuration
1. **Box Integration**: Connect Box enterprise account
2. **SharePoint/OneDrive**: Link Microsoft 365 sites
3. **Permission Mapping**: Configure user access rights
4. **Sync Settings**: Set scanning frequency and scope

#### Folder Selection
- **Browse Structure**: Navigate through connected repositories
- **Select Folders**: Choose specific directories for processing
- **Priority Settings**: Mark high-importance folders
- **Exclusions**: Skip specific paths or file types

### User Management

#### User Connections
- **View Status**: See which users have connected data sources
- **Connection History**: Track when users last authenticated
- **Token Management**: Monitor OAuth token expiration
- **Force Refresh**: Prompt users to re-authenticate

#### Access Control
- **Permission Levels**: Admin, Operator, Auditor, User
- **Tenant Isolation**: Ensure data separation
- **Group Management**: Manage access via Microsoft 365 groups
- **Audit Logs**: Track all access and changes

### System Controls

#### Ingestion Management
```bash
# Start ingestion process
POST /api/ingestion/start
{
  "tenant_id": "your-tenant",
  "source": "box",
  "mode": "incremental",
  "paths": ["/Finance", "/HR"]
}

# Stop ingestion process
POST /api/ingestion/stop
{
  "tenant_id": "your-tenant"
}

# Force rescan
POST /api/ingestion/rescan
{
  "tenant_id": "your-tenant",
  "paths": ["/specific-folder"],
  "mode": "full"
}
```

#### Processing Controls
- **Pipeline Status**: Monitor ingestion progress
- **Error Handling**: View and retry failed items
- **Performance Tuning**: Adjust processing parameters
- **Resource Limits**: Set memory and CPU constraints

### Monitoring and Analytics

#### Real-time Monitoring
- **Service Health**: Live status of all components
- **Performance Metrics**: Response times and throughput
- **Error Rates**: Failed requests and exceptions
- **Resource Usage**: Memory, CPU, and disk utilization

#### Usage Analytics
- **Query Patterns**: Most common question types
- **User Activity**: Peak usage times and volumes
- **Document Coverage**: Indexed vs. total documents
- **Cost Analysis**: Per-feature resource consumption

#### Audit and Compliance
- **Access Logs**: Who accessed what and when
- **Policy Decisions**: How sensitive data was handled
- **Security Events**: Unauthorized access attempts
- **Compliance Reports**: PII/PHI handling audit trails

## Common Workflows

### Document Discovery
1. **Ask General Questions**: "What documents do I have access to?"
2. **Refine Search**: "Show me documents from the Finance department"
3. **Content Analysis**: "What are the key points in the budget document?"
4. **Cross-reference**: "Which documents reference this project?"

### Policy Enforcement
1. **Review Policies**: Check current sensitive data rules
2. **Test Detection**: Upload sample content to validate
3. **Adjust Rules**: Modify patterns and behaviors
4. **Monitor Results**: Track policy effectiveness

### System Administration
1. **Health Check**: Review dashboard for issues
2. **User Support**: Help users connect data sources
3. **Performance Tuning**: Adjust system parameters
4. **Backup Verification**: Ensure data protection

## Troubleshooting

### Common Issues

#### Bot Not Responding
- Check if bot is added to Teams
- Verify user has proper permissions
- Ensure data sources are connected
- Check system health status

#### Missing Documents
- Verify folder permissions
- Check ingestion status
- Ensure documents are supported formats
- Review access control settings

#### Slow Responses
- Check system performance metrics
- Review query complexity
- Verify database performance
- Check network connectivity

### Getting Help
1. **Check Status**: Use `/status` command in Teams
2. **Admin Support**: Contact your system administrator
3. **Documentation**: Refer to this user guide
4. **System Logs**: Review error messages and logs

## Best Practices

### Query Optimization
- **Be Specific**: "Q4 budget for Engineering" vs. "budget"
- **Use Keywords**: Include relevant terms and dates
- **Limit Scope**: Focus on specific departments or time periods
- **Follow Up**: Ask related questions for deeper insights

### Data Management
- **Regular Updates**: Keep data sources connected
- **Permission Review**: Periodically verify access rights
- **Policy Updates**: Stay current with sensitive data rules
- **Usage Monitoring**: Track your query patterns

### Security Awareness
- **Verify Sources**: Ensure you're using official bot
- **Report Issues**: Alert admins to suspicious activity
- **Follow Policies**: Respect sensitive data handling rules
- **Log Out**: Sign out when using shared devices

## Advanced Features

### Custom Queries
```json
{
  "question": "Analyze budget trends",
  "filters": {
    "departments": ["Engineering", "Sales"],
    "time_range": "2024",
    "document_types": ["budget", "forecast"]
  },
  "output_format": "chart",
  "chart_type": "line"
}
```

### Batch Operations
- **Multiple Queries**: Submit several questions at once
- **Scheduled Reports**: Set up recurring document analysis
- **Export Results**: Download data in CSV or JSON format
- **Share Insights**: Collaborate with team members

### Integration Options
- **API Access**: Programmatic query interface
- **Webhooks**: Real-time notifications
- **Power BI**: Connect to business intelligence tools
- **Custom Apps**: Build specialized interfaces

## Next Steps
1. **Complete Setup**: Connect all data sources
2. **Explore Features**: Try different query types
3. **Customize Policies**: Configure sensitive data rules
4. **Train Users**: Share best practices with your team
5. **Monitor Usage**: Track system performance and costs

---
*Last Updated: 2025-01-27*
*Version: 1.0*
