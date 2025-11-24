"""QLDB resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class QLDBHandler(ResourceHandler):
    """Handler for Amazon QLDB resources."""

    @property
    def service_name(self) -> str:
        return "qldb"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all QLDB ledgers."""
        qldb = self.session.client("qldb")
        resources = []

        try:
            # List ledgers
            paginator = qldb.get_paginator("list_ledgers")
            for page in paginator.paginate():
                for ledger in page.get("Ledgers", []):
                    resources.append({
                        "id": ledger.get("Arn", ledger["Name"]),
                        "name": ledger["Name"],
                        "type": "ledger",
                        "state": ledger.get("State", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing QLDB ledgers: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a QLDB ledger."""
        qldb = self.session.client("qldb")
        ledger_name = resource.get("name")

        try:
            qldb.delete_ledger(Name=ledger_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting QLDB ledger {ledger_name}: {str(e)}"
            )
            return False
