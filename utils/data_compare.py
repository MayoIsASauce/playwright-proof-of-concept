import json
from re import search as re_search
from uuid import uuid4
from io import TextIOWrapper
from playwright.sync_api import Locator

class DataComp(object):
    def __init__(self, data_stream: TextIOWrapper):
        """Creates a new data comparer object
            data_stream: A file stream with a json object
            returns a new DataComp object with a stream loaded
        """
        self.__stream: dict[str, str] = json.loads("".join(data_stream.readlines()))
        self.__lock_stream = True

    def data_import(self, comparable: list[Locator]):
        """Import the data from a table identified by a Locator
           comparable: The table of data
           returns None
        """
        self.__imported_data: dict[str, str] = {}

        for row in comparable:
            headers = list(map(lambda h: h.inner_text(), row.locator("th").all()))

            def custom_map(loc: Locator):
                if (html := loc.element_handle().inner_html()).__contains__("input type=\"text\""):
                    matches = re_search(r'value="([^"]+@[^"]+)"', html)
                    return matches.group(1)
                return loc.inner_text()
            
            bodies = list(map(custom_map, row.locator("td").all()))
            
            for col in range(len(headers)):
                self.__imported_data[headers[col].replace("*", "")] = bodies[col]
        
        if self.__imported_data != {}:
            self.__lock_stream = False
    
    def data_test(self) -> bool:
        """Test the data from the table against the streamed data
            returns False if comparison fails otherwise True
        """
        if self.__lock_stream:
            raise ImportError("Please call `data_import` before test")

        KEYS = self.__stream['generalInfo'].keys()
        for KEY in KEYS:
            display_string = f"[{KEY}] expected '{self.__stream['generalInfo'][KEY]}' is actual '{self.__imported_data[KEY]}'"
            print(display_string)
            assert self.__stream['generalInfo'][KEY] == self.__imported_data[KEY], display_string

    def data_export(self, filename: str = None) -> None:
        """Export the current imported data to a json file
            filename: The name to use for the file, this can be left blank for default
            returns None
        """
        if self.__lock_stream:
            raise ImportError("Please call `data_import` before test")
        
        worker_file = f"exported-worker-{str(uuid4()).split("-")[0]}.json" if filename is None else filename

        with open(worker_file, "+x") as file:
            file.writelines(json.dumps(self.__imported_data))
