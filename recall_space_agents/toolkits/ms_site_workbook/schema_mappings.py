from pydantic import BaseModel, Field
from textwrap import dedent
from typing import List, Any, Dict

class ListWorksheetsInWorkbookSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    file_path: str = Field(
        ...,
        description=dedent("""
            Path to the Excel workbook file within the site's drive.
            For example: '/Documents/Folder1/workbook.xlsx'.
        """)
    )

class ListTablesInWorksheetSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    file_path: str = Field(
        ...,
        description=dedent("""
            Path to the Excel workbook file within the site's drive.
            For example: '/Documents/Folder1/workbook.xlsx'.
        """)
    )
    worksheet_name: str = Field(
        ...,
        description="Name of the worksheet within the Excel workbook."
    )

class GetTableContentSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    file_path: str = Field(
        ...,
        description=dedent("""
            Path to the Excel workbook file within the site's drive.
            For example: '/Documents/Folder1/workbook.xlsx'.
        """)
    )
    worksheet_name: str = Field(
        ...,
        description="Name of the worksheet within the Excel workbook."
    )
    table_name: str = Field(
        ...,
        description="Name of the table within the worksheet."
    )

class GetTableRowByIndexSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    file_path: str = Field(
        ...,
        description=dedent("""
            Path to the Excel workbook file within the site's drive.
            For example: '/Documents/Folder1/workbook.xlsx'.
        """)
    )
    worksheet_name: str = Field(
        ...,
        description="Name of the worksheet within the Excel workbook."
    )
    table_name: str = Field(
        ...,
        description="Name of the table within the worksheet."
    )
    index: int = Field(
        ...,
        description=dedent("""
            Zero-based index of the row to retrieve from the table.
            For example, '0' for the first data row in the table.
        """)
    )

class ListFilesAndFoldersSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    folder_path: str = Field(
        ...,
        description=dedent("""
            Path to the folder within the site's drive.
            For example: '/Documents/Folder1/'.
            Lists all files and folders within this path.
        """)
    )


class ApplyFilterToTableSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    file_path: str = Field(
        ...,
        description="Path to the file within the site's drive. For example: '/Folder1/file.xlsx'."
    )
    worksheet_name: str = Field(
        ...,
        description="The name of the worksheet."
    )
    table_name: str = Field(
        ...,
        description="The name of the table within the worksheet."
    )
    column_name: str = Field(
        ...,
        description="The name of the column to which the filter will be applied."
    )
    criteria: Any = Field(
        ...,
        description=dedent("""
            The filter criteria as a dictionary.

            Examples:

            Filtering by a single value:
                criteria = {
                    "filterOn": "Custom",
                    "criterion1": "=SomeValue"
                }

            Filtering by two values (e.g., "Value1" or "Value2"):
                criteria = {
                    "filterOn": "Custom",
                    "criterion1": "=Value1",
                    "operator": "Or",
                    "criterion2": "=Value2"
                }

            Filtering by a number greater than a value:
                criteria = {
                    "filterOn": "Custom",
                    "criterion1": ">10"
                }

            Filtering by dates between two values:
                criteria = {
                    "filterOn": "Custom",
                    "criterion1": ">=2021-01-01",
                    "operator": "And",
                    "criterion2": "<=2021-12-31"
                }
            """)
    )


class UpdateCellsValuesSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    file_path: str = Field(
        ...,
        description="Path to the file within the site's drive. For example: '/Folder1/file.xlsx'."
    )
    worksheet_name: str = Field(
        ...,
        description="The name of the worksheet where the cells are to be updated."
    )
    cells_to_update: Any = Field(
        ...,
        description=dedent("""
            A list of cells to update with their new values.

            Each entry should include:
            - 'cell_address': The address of the cell (e.g., 'B2').
            - 'cell_value': The new value to assign to the cell.

            Example:
                cells_to_update = [
                    {
                        "cell_address": "A1",
                        "cell_value": "New Value"
                    },
                    {
                        "cell_address": "B2",
                        "cell_value": 123
                    }
                ]
            """)
    )

class AddRowToTableSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    file_path: str = Field(
        ...,
        description="Path to the file within the site's drive. For example: '/Folder1/file.xlsx'."
    )
    worksheet_name: str = Field(
        ...,
        description="The name of the worksheet."
    )
    table_name: str = Field(
        ...,
        description="The name of the table within the worksheet."
    )
    row_values: List[Any] = Field(
        ...,
        description=dedent("""\
            The values to add as a new row in the table.

            Provide a list of values corresponding to the columns in the table.

            Example:
                row_values = ["Value1", "Value2", 123, "Value4"]
            """)
    )

schema_mappings = {
    "alist_worksheets_in_workbook": {
        "description": dedent("""
            List all worksheets in an Excel workbook.
            Given the site display name and path to the workbook file, 
            returns the names of all worksheets in the workbook.
        """),
        "input_schema": ListWorksheetsInWorkbookSchema,
    },
    "alist_tables_in_worksheet": {
        "description": dedent("""
            List all tables within a specified worksheet of an Excel workbook.
            Given the site display name, path to the workbook file, and worksheet name,
            returns the names of all tables in the worksheet.
        """),
        "input_schema": ListTablesInWorksheetSchema,
    },
    "aget_table_content": {
        "description": dedent("""
            Retrieve the content of a table in an Excel workbook as markdown.
            Given the site display name, path to the workbook file, worksheet name, and table name,
            returns the table's data formatted as markdown.
        """),
        "input_schema": GetTableContentSchema,
    },
    "aget_table_row_by_index": {
        "description": dedent("""
            Get a specific row from a table in an Excel workbook by index.
            Given the site display name, path to the workbook file, worksheet name, table name, and row index,
            returns the values in the specified row.
        """),
        "input_schema": GetTableRowByIndexSchema,
    },
    "alist_files_and_folders_in_path": {
        "description": dedent("""
            List the names of files and folders within a given path inside a SharePoint site's drive.
            Given the site display name and folder path, returns the names of all files and folders in that path.
        """),
        "input_schema": ListFilesAndFoldersSchema,
    },
    "aapply_filter_to_table": {
        "description": dedent("""
            This tool allows you to apply a filter to a table column based on specified criteria.
            """),
        "input_schema": ApplyFilterToTableSchema,
    },
    "aupdate_cells_values": {
        "description": dedent("""
            This tool updates specific cells in a worksheet to new values.
            """),
        "input_schema": UpdateCellsValuesSchema,
    },
    "aadd_row_to_table": {
        "description": dedent("""
            This tool adds a new row with specified values to a table within a workbook.
            """),
        "input_schema": AddRowToTableSchema,
    },
}