# Java to C++ Code Translator
## Project Assumptions

### General Program Goals
The program serves as an automatic translator for converting Java source code into its C++ equivalent. It preserves class structures, methods, and fields while adapting Java-specific constructs to their C++ counterparts.

### Translator Type
Compiler - the program translates Java source code into C++ source code.

### Expected Program Output
A converter (compiler) from Java to C++ that:
- Transforms Java classes into C++ classes
- Adapts Java collections to STL containers
- Converts System.out.println to std::cout
- Maintains program control structure (if, for, while)
- Generates syntactically correct C++ code

### Implementation Language
Python 3

### Scanner/Parser Implementation
ANTLR4 parser generator was chosen due to:
- Python target language support
- Built-in Visitor pattern support

## Token Description
```antlr
CLASS: 'class';
PUBLIC: 'public';
PRIVATE: 'private';
PROTECTED: 'protected';
IF: 'if';
ELSE: 'else';
FOR: 'for';
WHILE: 'while';
RETURN: 'return';
 ... more tokens available in JavaLexerr.g4 file
```

## Format Grammar
```antlr
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
    ; ... more grammar rules available in JavaGrammar.g4 file
```

## Used Generators and External Packages
1. ANTLR4 (antlr4-python3-runtime)
   - Parser and lexer generator
   - Version: 4.9.3
2. Python 3
   - Implementation language
   - Generic type usage

## User Manual
1. Install required packages:
```bash
pip install antlr4-python3-runtime
```
2. Compile the grammar:
```bash
java -jar lib/antlr-4.13.1-complete.jar -Dlanguage=Python3 -o src/gen src/JavaGrammar.g4
java -jar lib/antlr-4.13.1-complete.jar -Dlanguage=Python3 -o src/gen src/JavaLexer.g4  

```  

3. Run the translator:
```bash
python translate.py --input test.java --output test.cpp
```
Parameters:
- `--input`: path to input file (Java)
- `--output`: path to output file (C++)

4. Try to compile generated code:
```bash
g++ -c -std=c++20 -mconsole test.cpp
```
## Usage Example

### Input Code (Java):
```java
class Simple {
    private int number;

    public Simple(int number) {
        this.number = number;
    }

    public void increment() {
        number++;
        System.out.println("Number: " + number);
    }
}

```

### Generated Code (C++):
```cpp
#include <iostream>

class Simple {
private:
    int number;

public:
    Simple(int number) : number(number) {
    }

    void increment() {
        number++;
        std::cout << "Number: " << number << std::endl;
    }
};

```

## Additional Information
1. Supported Language Constructs:
   - Classes and their members
   - Basic data types
   - Control statements
   - Operators
   - Java collections (List, Set, Map)

2. Limitations:
   - No support for nested classes
   - No exception handling
   - No lambda expression support
   - No for-each
   - No more advanced Java syntax support
