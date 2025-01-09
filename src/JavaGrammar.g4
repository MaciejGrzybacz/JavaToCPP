parser grammar JavaGrammar;

options {
    tokenVocab = JavaLexer;
}

start: compilationUnit EOF;

compilationUnit
    : (comment | packageDeclaration)?
      (comment | importDeclaration)*
      (comment | typeDeclaration)*
    ;

comment: COMMENT;

packageDeclaration
    : PACKAGE qualifiedName SEMI
    ;

importDeclaration
    : IMPORT qualifiedName (DOT Identifier)? SEMI
    ;

typeDeclaration
    : classDeclaration
    | SEMI
    ;

classDeclaration
    : comment* modifier* CLASS Identifier classBody
    ;

classBody
    : LBRACE classBodyDeclaration* RBRACE
    ;

classBodyDeclaration
    : comment* SEMI
    | comment* modifier* memberDeclaration
    ;

memberDeclaration
    : methodDeclaration
    | fieldDeclaration
    | constructorDeclaration
    ;

methodDeclaration
    : comment* (typeRule | VOID) Identifier formalParameters methodBody
    ;

constructorDeclaration
    : comment* modifier* Identifier formalParameters constructorBody
    ;

methodBody
    : block
    | SEMI
    ;

constructorBody
    : LBRACE blockStatement* RBRACE
    ;

block
    : LBRACE (comment | blockStatement)* RBRACE
    ;

blockStatement
    : comment* localVariableDeclaration SEMI
    | comment* statement
    ;

statement
    : block                                      #blockStmt
    | printlnStatement                           #printlnStmt
    | IF parExpression statement
      (ELSE statement)?                          #ifStmt
    | FOR LPAREN forControl RPAREN statement     #forStmt
    | WHILE parExpression statement              #whileStmt
    | RETURN expression? SEMI                    #returnStmt
    | BREAK SEMI                                 #breakStmt
    | CONTINUE SEMI                              #continueStmt
    | SEMI                                       #emptyStmt
    | statementExpression SEMI                   #expressionStmt
    ;

forControl
    : forInit? SEMI expression? SEMI forUpdate?
    ;

forInit
    : localVariableDeclaration
    | expressionList
    ;

forUpdate
    : expressionList
    | expression INC
    | expression DEC
    ;

printlnStatement
    : PRINTLN LPAREN expressionList? RPAREN SEMI
    ;

expressionList
    : expression (COMMA expression)*
    ;

localVariableDeclaration
    : comment* modifier* typeRule variableDeclarators
    ;

variableDeclarators
    : variableDeclarator (COMMA variableDeclarator)*
    ;

variableDeclarator
    : variableDeclaratorId (ASSIGN variableInitializer)?
    ;

variableDeclaratorId
    : Identifier (LBRACK RBRACK)*
    ;

variableInitializer
    : expression
    ;

parExpression
    : LPAREN expression RPAREN
    ;

statementExpression
    : expression
    ;

expression
    : NEW creator                                         #newExpr
    | primary                                             #primaryExpr
    | expression DOT Identifier                           #dotExpr
    | expression DOT methodInvocation                     #methodCallExpr
    | methodInvocation                                    #methodInvocationExpr
    | expression LBRACK expression RBRACK                 #arrayAccessExpr
    | expression (MUL | DIV) expression                   #multiplicativeExpr
    | expression (ADD | SUB) expression                   #additiveExpr
    | expression (LT | GT) expression                     #relationalExpr
    | expression EQUAL expression                         #equalityExpr
    | expression AND expression                           #andExpr
    | expression OR expression                            #orExpr
    | expression ASSIGN expression                        #assignmentExpr
    | INC expression                                      #prefixIncrementExpr
    | DEC expression                                      #prefixDecrementExpr
    | expression INC                                      #postfixIncrementExpr
    | expression DEC                                      #postfixDecrementExpr
    | LPAREN expression RPAREN                            #parenthesizedExpr
    ;

methodInvocation
    : Identifier LPAREN expressionList? RPAREN
    ;

primary
    : literal                                             #literalExpr
    | Identifier                                          #identifierExpr
    | THIS                                                #thisExpr
    ;

creator
    : createdName (typeArgumentsOrDiamond)? (arrayCreatorRest | constructorCall)
    ;

typeArgumentsOrDiamond
    : typeArguments
    | LT GT
    ;

constructorCall
    : LPAREN expressionList? RPAREN
    ;

arrayCreatorRest
    : LBRACK expression RBRACK
    ;

createdName
    : Identifier
    | primitiveType
    ;

typeArguments
    : LT typeList GT
    | LT GT
    ;

typeList
    : typeRule (COMMA typeRule)*
    ;

formalParameters
    : LPAREN formalParameterList? RPAREN
    ;

formalParameterList
    : formalParameter (COMMA formalParameter)*
    ;

formalParameter
    : comment* modifier* typeRule variableDeclaratorId
    ;

typeRule
    : primitiveType (LBRACK RBRACK)*
    | Identifier typeArguments? (LBRACK RBRACK)*
    ;

primitiveType
    : BOOLEAN
    | INT
    | FLOAT
    ;

fieldDeclaration
    : comment* typeRule variableDeclarators SEMI
    ;

modifier
    : PUBLIC
    | PRIVATE
    | PROTECTED
    | STATIC
    | FINAL
    ;

qualifiedName
    : Identifier (DOT Identifier)*
    ;

literal
    : IntegerLiteral
    | FloatingPointLiteral
    | StringLiteral
    | BooleanLiteral
    ;