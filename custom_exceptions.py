class GoogleSheetException(Exception):
    def __init__(self, message="An error occurred when accessing the Google Sheets API"):
        super().__init__(message)

class FirestoreException(Exception):
    def __init__(self, message="An error occurred when accessing the Firestore API"):
        super().__init__(message)
