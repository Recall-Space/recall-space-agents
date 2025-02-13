import json
from typing import Any, Dict, List

import pandas as pd

from recall_space_agents.toolkits.ms_site.ms_site import MSSiteToolKit
from recall_space_agents.toolkits.ms_site_workbook.schema_mappings import \
    schema_mappings
from recall_space_agents.utils.dataframe_to_markdown import \
    dataframe_to_markdown


class MSSiteWorkbookToolKit(MSSiteToolKit):
    def __init__(self, credentials):
        self.credentials = credentials
        super().__init__(credentials)
        self.schema_mappings = schema_mappings

    async def alist_files_and_folders_in_path(
        self, site_display_name: str, folder_path: str
    ):
        """
        Asynchronously list files and folders in a specified path.

        Args:
            site_display_name (str): The display name of the SharePoint site.
            folder_path (str): The path to the folder within the SharePoint site,
            starting from the root.

        Returns:
            list or str: A list of item names within the folder, or an error
            message if the operation fails.
        """
        folder_path = self._remove_document_prefix(folder_path)
        site_id = await self.get_site_id(site_display_name)
        if not site_id:
            return f"Site with display name '{site_display_name}' not found."

        drive_id = await self.get_drive_id(site_id)
        if not drive_id:
            return f"Drive not found for site with ID '{site_id}'."

        folders = folder_path.strip("/").split("/")

        folder_id = "root"
        for folder in folders:
            children = (
                await self.ms_graph_client.drives.by_drive_id(drive_id)
                .items.by_drive_item_id(folder_id)
                .children.get()
            )
            folder_id = None
            for child in children.value:
                if child.name == folder:
                    folder_id = child.id
                    break
            if not folder_id:
                return f"Folder '{folder}' not found."

        children = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(folder_id)
            .children.get()
        )
        item_names = [child.name for child in children.value]
        return item_names

    async def alist_worksheets_in_workbook(
        self, site_display_name: str, file_path: str
    ):
        """
        List all worksheets in a workbook.

        Args:
            site_display_name (str): The display name of the SharePoint site.
            file_path (str): The path to the file within the site.

        Returns:
            worksheet names: A list of worksheets names.
        """
        site_id = await self.get_site_id(display_name=site_display_name)
        if not site_id:
            raise ValueError(f"Site '{site_display_name}' not found.")
        drive_id = await self.get_drive_id(site_id=site_id)
        if not drive_id:
            raise ValueError(f"Drive not found for site '{site_display_name}'.")
        file_id = await self.get_file_id_by_path(drive_id=drive_id, file_path=file_path)
        if not file_id:
            raise ValueError(f"File '{file_path}' not found in drive.")

        worksheets = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.get()
        )
        worksheet_names = [each.name for each in worksheets.value]
        return worksheet_names

    async def alist_tables_in_worksheet(
        self, site_display_name: str, file_path: str, worksheet_name: str
    ):
        """
        List all tables in a specified worksheet.

        Args:
            site_display_name (str): The display name of the SharePoint site.
            file_path (str): The path to the file within the site.
            worksheet_name (str): The name of the worksheet.

        Returns:
            List[WorkbookTable]: A list of tables in the worksheet.
        """
        site_id = await self.get_site_id(display_name=site_display_name)
        if not site_id:
            raise ValueError(f"Site '{site_display_name}' not found.")
        drive_id = await self.get_drive_id(site_id=site_id)
        if not drive_id:
            raise ValueError(f"Drive not found for site '{site_display_name}'.")
        file_id = await self.get_file_id_by_path(drive_id=drive_id, file_path=file_path)
        if not file_id:
            raise ValueError(f"File '{file_path}' not found in drive.")

        # Get the worksheet
        worksheets = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.get()
        )
        worksheet_id = None
        for ws in worksheets.value:
            if ws.name == worksheet_name:
                worksheet_id = ws.id
                break
        if not worksheet_id:
            raise ValueError(f"Worksheet '{worksheet_name}' not found in workbook.")

        tables = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.by_workbook_worksheet_id(worksheet_id)
            .tables.get()
        )
        tables_names = [each.name for each in tables.value]
        return tables_names

    async def aget_table_content(
        self,
        site_display_name: str,
        file_path: str,
        worksheet_name: str,
        table_name: str,
    ):
        """
        Get the content of a table by its name in a specified worksheet.

        Args:
            site_display_name (str): The display name of the SharePoint site.
            file_path (str): The path to the file within the site.
            worksheet_name (str): The name of the worksheet.
            table_name (str): The name of the table.

        Returns:
            List[List[Any]]: The values in the table.
        """
        site_id = await self.get_site_id(display_name=site_display_name)
        if not site_id:
            raise ValueError(f"Site '{site_display_name}' not found.")
        drive_id = await self.get_drive_id(site_id=site_id)
        if not drive_id:
            raise ValueError(f"Drive not found for site '{site_display_name}'.")
        file_id = await self.get_file_id_by_path(drive_id=drive_id, file_path=file_path)
        if not file_id:
            raise ValueError(f"File '{file_path}' not found in drive.")

        # Get the worksheet
        worksheets = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.get()
        )
        worksheet_id = None
        for ws in worksheets.value:
            if ws.name == worksheet_name:
                worksheet_id = ws.id
                break
        if not worksheet_id:
            raise ValueError(f"Worksheet '{worksheet_name}' not found in workbook.")

        # Get the table
        tables = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.by_workbook_worksheet_id(worksheet_id)
            .tables.get()
        )
        table_id = None
        for table in tables.value:
            if table.name == table_name:
                table_id = table.id
                break
        if not table_id:
            raise ValueError(
                f"Table '{table_name}' not found in worksheet '{worksheet_name}'."
            )

        # Get the content of the table
        # it includes rows
        table_columns = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.tables.by_workbook_table_id(table_id)
            .columns.get()
        )
        table_content = table_columns.value
        table_dict = {}
        for each in table_content:
            table_dict[each.additional_data['values'][0][0]]=[each[0] for each in each.additional_data['values'][1:]]
        table_dataframe = pd.DataFrame(table_dict)
        table_markdown = dataframe_to_markdown(table_dataframe)
        return table_markdown

    async def aget_table_row_by_index(
        self,
        site_display_name: str,
        file_path: str,
        worksheet_name: str,
        table_name: str,
        index: int,
    ):
        """
        Get a specific row of a table by index.

        Args:
            site_display_name (str): The display name of the SharePoint site.
            file_path (str): The path to the file within the site.
            worksheet_name (str): The name of the worksheet.
            table_name (str): The name of the table.
            index (int): The index of the row (starting from 0).

        Returns:
            List[Any]: The values in the row.
        """
        # Get IDs as before
        site_id = await self.get_site_id(display_name=site_display_name)
        if not site_id:
            raise ValueError(f"Site '{site_display_name}' not found.")
        drive_id = await self.get_drive_id(site_id=site_id)
        if not drive_id:
            raise ValueError(f"Drive not found for site '{site_display_name}'.")
        file_id = await self.get_file_id_by_path(drive_id=drive_id, file_path=file_path)
        if not file_id:
            raise ValueError(f"File '{file_path}' not found in drive.")

        # Get the worksheet
        worksheets = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.get()
        )
        worksheet_id = None
        for ws in worksheets.value:
            if ws.name == worksheet_name:
                worksheet_id = ws.id
                break
        if not worksheet_id:
            raise ValueError(f"Worksheet '{worksheet_name}' not found in workbook.")

        # Get the table
        tables = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.by_workbook_worksheet_id(worksheet_id)
            .tables.get()
        )
        table_id = None
        for table in tables.value:
            if table.name == table_name:
                table_id = table.id
                break
        if not table_id:
            raise ValueError(
                f"Table '{table_name}' not found in worksheet '{worksheet_name}'."
            )

        # Get the row by index
        row = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.tables.by_workbook_table_id(table_id)
            .rows.item_at_with_index(index)
            .get()
        )
        row_table_by_index = row.additional_data["values"][0]
        return row_table_by_index

    async def aapply_filter_to_table(
        self,
        site_display_name: str,
        file_path: str,
        worksheet_name: str,
        table_name: str,
        column_name: str,
        criteria: dict,
    ):
        """
        Apply a filter to a table column.

        Args:
            site_display_name (str): The display name of the SharePoint site.
            file_path (str): The path to the file within the site.
            worksheet_name (str): The name of the worksheet.
            table_name (str): The name of the table.
            column_name (str): The name of the column to filter.
            criteria (dict): The filter criteria as a dictionary.

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

        Returns:
            str: Confirmation message indicating that the filter has been applied.

        Raises:
            ValueError: If the site, drive, file, worksheet, table, or column is not found.
            Exception: If the filter application fails due to an API error.
        """
        import aiohttp

        # Get IDs as before
        site_id = await self.get_site_id(display_name=site_display_name)
        if not site_id:
            raise ValueError(f"Site '{site_display_name}' not found.")
        drive_id = await self.get_drive_id(site_id=site_id)
        if not drive_id:
            raise ValueError(f"Drive not found for site '{site_display_name}'.")
        file_id = await self.get_file_id_by_path(drive_id=drive_id, file_path=file_path)
        if not file_id:
            raise ValueError(f"File '{file_path}' not found in drive.")

        # Get the worksheet
        worksheets = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.get()
        )
        worksheet_id = None
        for ws in worksheets.value:
            if ws.name == worksheet_name:
                worksheet_id = ws.id
                break
        if not worksheet_id:
            raise ValueError(f"Worksheet '{worksheet_name}' not found in workbook.")

        # Get the table
        tables = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.by_workbook_worksheet_id(worksheet_id)
            .tables.get()
        )
        table_id = None
        for table in tables.value:
            if table.name == table_name:
                table_id = table.id
                break
        if not table_id:
            raise ValueError(
                f"Table '{table_name}' not found in worksheet '{worksheet_name}'."
            )

        # Get the column
        columns = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.tables.by_workbook_table_id(table_id)
            .columns.get()
        )
        column_id = None
        for col in columns.value:
            if col.name == column_name:
                column_id = col.id
                break
        if not column_id:
            raise ValueError(
                f"Column '{column_name}' not found in table '{table_name}'."
            )

        # Prepare the API request to apply filter
        access_token = self.credentials.get_token(*self.required_scopes_as_user)
        headers = {
            "Authorization": f"Bearer {access_token.token}",
            "Content-Type": "application/json",
        }

        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/workbook/tables/{table_id}/columns/{column_id}/filter/apply"

        payload = {"criteria": criteria}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in (200, 204):
                    text = await response.text()
                    raise Exception(
                        f"Failed to apply filter: {response.status}, {text}"
                    )
        filtered_table_json_str = await self.aget_filtered_table_data(
            site_display_name=site_display_name,
            file_path=file_path,
            worksheet_name=worksheet_name,
            table_name=table_name)
        #clean filters
        await self.ms_graph_client.drives.by_drive_id(
            drive_id).items.by_drive_item_id(
                file_id).workbook.tables.by_workbook_table_id(
                    table_id).columns.by_workbook_table_column_id(column_id).filter.clear.post()
        
        return filtered_table_json_str

    async def aget_filtered_table_data(
        self,
        site_display_name: str,
        file_path: str,
        worksheet_name: str,
        table_name: str,
    ):
        """
        Get the data of the table's visible range after applying a filter.

        Args:
            site_display_name (str): The display name of the SharePoint site.
            file_path (str): The path to the file within the site.
            worksheet_name (str): The name of the worksheet.
            table_name (str): The name of the table.

        Returns:
            Dict: A dictionary containing the filtered data and the range.
        """
        # Get IDs as before
        site_id = await self.get_site_id(display_name=site_display_name)
        drive_id = await self.get_drive_id(site_id=site_id)
        file_id = await self.get_file_id_by_path(drive_id=drive_id, file_path=file_path)

        # Get worksheet ID
        worksheets = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.get()
        )
        worksheet_id = None
        for ws in worksheets.value:
            if ws.name == worksheet_name:
                worksheet_id = ws.id
                break
        if not worksheet_id:
            raise ValueError(f"Worksheet '{worksheet_name}' not found in workbook.")

        # Get table ID
        tables = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.by_workbook_worksheet_id(worksheet_id)
            .tables.get()
        )
        table_id = None
        for table in tables.value:
            if table.name == table_name:
                table_id = table.id
                break
        if not table_id:
            raise ValueError(
                f"Table '{table_name}' not found in worksheet '{worksheet_name}'."
            )

        # Get the visible range of the table after filtering
        rows_in_table_view = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.tables.by_workbook_table_id(table_id)
            .range.visible_view.get()
        )

        # Extract cell addresses and values
        filtered_view_row_addresses = rows_in_table_view.additional_data[
            "cellAddresses"
        ]
        filtered_view_row_values = rows_in_table_view.additional_data["values"]

        # Map cell addresses to their corresponding values
        cell_data = {}
        for row_addresses, row_values in zip(
            filtered_view_row_addresses, filtered_view_row_values
        ):
            for address, value in zip(row_addresses, row_values):
                cell_data[address] = value

        # Determine the general range of the response table (e.g., 'A1:R4')
        start_cell = filtered_view_row_addresses[0][0]
        end_cell = filtered_view_row_addresses[-1][-1]
        general_range = f"{start_cell}:{end_cell}"
        response_dict = {"range": general_range, "cell_data": cell_data}
        # Convert the dictionary to a JSON string
        response_string = json.dumps(response_dict, indent=4)

        return response_string

    async def aupdate_cells_values(
        self,
        site_display_name: str,
        file_path: str,
        worksheet_name: str,
        cells_to_update: List[Dict[str, Any]],
    ):
        """
        Update the values of multiple specific cells.

        Args:
            site_display_name (str): The display name of the SharePoint site.
            file_path (str): The path to the file within the site.
            worksheet_name (str): The name of the worksheet.
            cells_to_update (List[Dict[str, Any]]): A list of dictionaries with 'cell_address' and 'cell_value'.

        Returns:
            None
        """
        import aiohttp

        # Get IDs as before
        site_id = await self.get_site_id(display_name=site_display_name)
        drive_id = await self.get_drive_id(site_id=site_id)
        file_id = await self.get_file_id_by_path(drive_id=drive_id, file_path=file_path)

        # Get worksheet ID
        worksheets = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.get()
        )

        worksheet_id = None
        for ws in worksheets.value:
            if ws.name == worksheet_name:
                worksheet_id = ws.id
                break
        if not worksheet_id:
            raise ValueError(f"Worksheet '{worksheet_name}' not found in workbook.")

        # Prepare headers for API requests
        access_token = self.credentials.get_token(*self.required_scopes_as_user)
        headers = {
            "Authorization": f"Bearer {access_token.token}",
            "Content-Type": "application/json",
        }

        # Update each cell individually
        async with aiohttp.ClientSession() as session:
            for cell_update in cells_to_update:
                cell_address = cell_update["cell_address"]
                new_value = cell_update["cell_value"]

                url = (
                    f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/"
                    f"workbook/worksheets/{worksheet_id}/range(address='{cell_address}')"
                )

                payload = {"values": [[new_value]]}

                # Send the PATCH request to update the cell value
                async with session.patch(
                    url, headers=headers, json=payload
                ) as response:
                    if response.status not in (200, 204):
                        text = await response.text()
                        raise Exception(
                            f"Failed to update cell {cell_address}: {response.status}, {text}"
                        )
        return "Cells were successfully updated"

    async def aadd_row_to_table(
        self,
        site_display_name: str,
        file_path: str,
        worksheet_name: str,
        table_name: str,
        row_values: List[Any],
    ):
        """
        Add a row to a table.

        Args:
            site_display_name (str): The display name of the SharePoint site.
            file_path (str): The path to the file within the site.
            worksheet_name (str): The name of the worksheet.
            table_name (str): The name of the table.
            row_values (List[Any]): The values to add as a new row.

        Returns:
            None
        """
        import aiohttp

        # Get IDs as before
        site_id = await self.get_site_id(display_name=site_display_name)
        drive_id = await self.get_drive_id(site_id=site_id)
        file_id = await self.get_file_id_by_path(drive_id=drive_id, file_path=file_path)

        # Get worksheet ID
        worksheets = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.get()
        )
        worksheet_id = None
        for ws in worksheets.value:
            if ws.name == worksheet_name:
                worksheet_id = ws.id
                break
        if not worksheet_id:
            raise ValueError(f"Worksheet '{worksheet_name}' not found in workbook.")

        # Get table ID
        tables = (
            await self.ms_graph_client.drives.by_drive_id(drive_id)
            .items.by_drive_item_id(file_id)
            .workbook.worksheets.by_workbook_worksheet_id(worksheet_id)
            .tables.get()
        )
        table_id = None
        for table in tables.value:
            if table.name == table_name:
                table_id = table.id
                break
        if not table_id:
            raise ValueError(
                f"Table '{table_name}' not found in worksheet '{worksheet_name}'."
            )

        # Add the row
        access_token = self.credentials.get_token(*self.required_scopes_as_user)
        headers = {
            "Authorization": f"Bearer {access_token.token}",
            "Content-Type": "application/json",
        }

        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/workbook/tables/{table_id}/rows"

        payload = {"values": [row_values]}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in (200, 201, 204):
                    text = await response.text()
                    raise Exception(
                        f"Failed to add row to table: {response.status}, {text}"
                    )
        return 'the row has been successfully added'

