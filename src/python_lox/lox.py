from .lexer import Lexer
class Lox:
    version = '0.1.0'
    build_date = '12 April 2025 17:01:30'
    
    def run(self, source: str) -> int:
        """
        Execute the source program
        """
        lexer = Lexer(source)
        for token in lexer.process():
            print(token)

        return 0
