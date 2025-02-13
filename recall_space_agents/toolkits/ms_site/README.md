# MSSiteToolKit  

`MSSiteToolKit` is a Python module that provides asynchronous methods to interact with Microsoft SharePoint sites and files via the Microsoft Graph API. It allows you to extract text from files, search for files, and list files and folders within a SharePoint site. Additionally, it integrates with tool builders for agent-based applications.  

## Features  

- **Extract Text from Files**: Extract text content from files such as PDFs, DOCXs, and XLSXs given the site name and file path.  
- **Search and Extract Text**: Search for a file by name and extract its text content.  
- **List Files and Folders**: List files and folders in a specified path within a SharePoint site.  
- **Integration with Agent Tools**: Provides tool definitions compatible with agent builders for seamless integration.  

## Prerequisites  

- Python 3.7 or higher  
- An Azure AD application with the following Microsoft Graph API permissions:  
  - `Sites.Read.All`  
  - `Sites.ReadWrite.All`  
- **Microsoft Graph SDK for Python**:  
  - Install via pip: `pip install msgraph-sdk`  
- **Pydantic** for data validation:  
  - Install via pip: `pip install pydantic`  
- **Agent Builder** (from `agent_builder.builders.tool_builder`), if integrating with agent-based applications. 