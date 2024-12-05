grammar Java;

// Parser rules
program
    : importDeclaration* classDeclaration EOF
    ;

importDeclaration
    : 'import' javaDotIdentifier ';'
    ;

javaDotIdentifier
    : ID ('.' ID)*
    ;

classDeclaration
    : modifier* 'class' ID '{' member* '}'
    ;

member
    : fieldDeclaration
    | methodDeclaration
    ;

modifier
    : 'public'
    | 'private'
    | 'protected'
    | 'static'
    ;

fieldDeclaration
    : modifier* type ID ';'
    ;

methodDeclaration
    : modifier* type ID '(' paramList? ')' '{' statement* '}'
    ;

paramList
    : param (',' param)*
    ;

param
    : type ID
    ;

type
    : simpleType
    | genericType
    ;

simpleType
    : 'int'
    | 'void'
    | 'String'
    | ID
    ;

genericType
    : ID '<' type '>'
    ;

statement
    : ID '=' expression ';'
    | expression ';'
    | 'return' expression? ';'
    | variableDeclaration ';'
    | forStatement
    ;

forStatement
    : 'for' '(' forControl ')' '{' statement* '}'
    ;

forControl
    : forInit? ';' expression? ';' forUpdate?
    ;

forInit
    : variableDeclaration
    | expression
    ;

forUpdate
    : expression
    ;

variableDeclaration
    : type ID ('=' expression)?
    ;

expression
    : primary expressionRest*
    ;

expressionRest
    : '.' ID '(' expressionList? ')'
    | '.' ID
    | '+' expression
    | '*' expression
    | '<' expression
    | '>' expression
    | '<=' expression
    | '>=' expression
    | '==' expression
    | '!=' expression
    | '++'
    | '--'
    ;

primary
    : ID
    | NUMBER
    | STRING
    | ID '(' expressionList? ')'
    | 'new' type '(' expressionList? ')'
    | '(' expression ')'
    | 'System' '.' 'out' '.' ('println' | 'print') '(' expression ')'
    | '++' ID
    | '--' ID
    ;

expressionList
    : expression (',' expression)*
    ;

// Lexer rules
ID: [a-zA-Z_][a-zA-Z_0-9]* ;
NUMBER: [0-9]+ ;
STRING: '"' .*? '"' ;
WS: [ \t\r\n]+ -> skip ;
COMMENT: '//' .*? '\r'? '\n' -> skip ;
MULTILINE_COMMENT: '/*' .*? '*/' -> skip ;