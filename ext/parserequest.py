import re

class ParseRequest():
    """
    Parse the user messages and decides what kind 
    of request is
    """

    __BAG_OF_HELLO_WORDS = ['hello', 'hi', ':wave:' 'good day', 'good morning']
    __BAG_OF_HELP_WORDS = ['help', 'helpme']
    __BAG_OF_ACTION_WORDS = ['save', 'action', 'file']

    def __init__(self, text):
        self._text = text
    
    def is_hello_request(self):
        """
        This is an hello request. 
        Bot has to reply with an hello
        """
        return self._is_request(self._text, self.__BAG_OF_HELLO_WORDS)
    

    def is_action_request(self):
        """
        This is an action request.
        Bot has to show the interactive dialog
        """
        return self._is_request(self._text, self.__BAG_OF_ACTION_WORDS)
    
    def is_help_request(self):
        """
        This is an help requst.
        Bot return with a list of commands available
        """
        return self._is_request(self._text, self.__BAG_OF_HELP_WORDS)
    
    def _is_request(self, text, bag_of_words):
        """
        If the message has one of the keyword in the list
        return True.
        """
        text = re.sub('[.,;!?-_\'"]','',text.lower())
        text_list = text.split()
        for word in bag_of_words:
            if word in text_list:
                return True
        return False   