from typing import Dict, List, Any

from time_utils import *


class NetWorthDataClass:
    def __init__(self, assets: float, liabilities: float, net_worth: float, date: datetime = None):
        self.assets: float = assets
        self.liabilities: float = liabilities
        self.net_worth: float = net_worth

        if not date:
            self.date: datetime = get_todays_date_only()
        else:
            self.date: datetime = date

    def to_firestore_dict(self) -> Dict[str, float | datetime]:
        return {
            "assets": self.assets,
            "liabilities": self.liabilities,
            "net_worth": self.net_worth,
            "date": self.date
        }

    def to_sheets_list(self) -> List[List[str]]:
        return [[get_formatted_local_date(), str(self.assets), str(self.liabilities), str(self.net_worth)]]


class HoldingsDataClass:
    def __init__(self, holdings: Dict[str, float], date: datetime = None):
        self.holdings = holdings

        if not date:
            self.date: datetime = get_todays_date_only()
        else:
            self.date: datetime = date

    def to_firestore_dict(self) -> Dict[str, Dict[str, float] | datetime]:
        return {
            "holdings": self.holdings,
            "date": self.date
        }

    def to_sheets_list(self) -> Any:
        return []
