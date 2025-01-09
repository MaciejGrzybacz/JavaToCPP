lexer grammar JavaLexer;

// Keywords
PACKAGE : 'package';
IMPORT : 'import';
PUBLIC : 'public';
PRIVATE : 'private';
PROTECTED : 'protected';
STATIC : 'static';
CLASS : 'class';
VOID : 'void';
NEW : 'new';
THIS : 'this';
IF : 'if';
ELSE : 'else';
FOR : 'for';
WHILE : 'while';
RETURN : 'return';
BREAK : 'break';
CONTINUE : 'continue';
PRINTLN : 'System.out.println';
FINAL : 'final';
BOOLEAN : 'boolean';
INT : 'int';
FLOAT : 'float';

// Separators
LPAREN : '(';
RPAREN : ')';
LBRACE : '{';
RBRACE : '}';
LBRACK : '[';
RBRACK : ']';
SEMI : ';';
COMMA : ',';
DOT : '.';
COLON : ':';

// Operators
ASSIGN : '=';
GT : '>';
LT : '<';
EQUAL : '==';
AND : '&&';
OR : '||';
INC : '++';
DEC : '--';
ADD : '+';
SUB : '-';
MUL : '*';
DIV : '/';

// Basic tokens
Identifier
    : JavaLetter JavaLetterOrDigit*
    ;

fragment
JavaLetter
    : [a-zA-Z$_]
    ;

fragment
JavaLetterOrDigit
    : [a-zA-Z0-9$_]
    ;

// Literals
IntegerLiteral
    : DecimalIntegerLiteral
    ;

fragment
DecimalIntegerLiteral
    : DecimalNumeral
    ;

fragment
DecimalNumeral
    : '0'
    | [1-9] [0-9]*
    ;

FloatingPointLiteral
    : DecimalFloatingPointLiteral
    ;

fragment
DecimalFloatingPointLiteral
    : DecimalNumeral '.' [0-9]* ExponentPart?
    | '.' [0-9]+ ExponentPart?
    | DecimalNumeral ExponentPart
    ;

fragment
ExponentPart
    : [eE] [+-]? [0-9]+
    ;

BooleanLiteral
    : 'true'
    | 'false'
    ;

StringLiteral
    : '"' StringCharacter* '"'
    ;

NullLiteral
    : 'null'
    ;

fragment
StringCharacter
    : ~["\\\r\n]
    | EscapeSequence
    ;

fragment
EscapeSequence
    : '\\' [btnfr"'\\]
    ;

// Comments
COMMENT
    : '//' ~[\r\n]* -> channel(HIDDEN)
    ;

// Whitespace
WS
    : [ \t\r\n\u000C]+ -> skip
    ;

// Error handling
ERROR : . ;