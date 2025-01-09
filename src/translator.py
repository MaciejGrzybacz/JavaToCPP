from antlr4 import *
from gen.JavaLexer import JavaLexer
from gen.JavaGrammar import JavaGrammar
from typing import List, Set, Dict
import os


class BaseVisitor:
    def visit(self, node):
        if node is None:
            return ""
        if isinstance(node, list):
            return [self.visit(n) for n in node]

        if hasattr(node, 'COMMENT'):
            comment = node.getText()
            self.output.append(f"{self.indent_str()}{comment}")
            return ""

        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        result = visitor(node)
        return result if result is not None else ""

    def generic_visit(self, node):
        if hasattr(node, 'getChildren'):
            for child in node.getChildren():
                self.visit(child)
        return ""


class JavaToCppTranslator(BaseVisitor):
    def __init__(self):
        self.output = []
        self.current_indent = 0
        self.required_includes = {"#include <iostream>"}
        self.class_fields = {}
        self.local_variables = {}
        self.current_class = None
        self.includes = {
            'String': 'string',
            'List': 'vector',
            'ArrayList': 'vector',
            'Map': 'map',
            'HashMap': 'unordered_map',
            'Set': 'set',
            'HashSet': 'unordered_set'
        }
        self.collection_methods = {
            'std::vector': {
                'add': 'push_back',
                'get': 'at',
                'size': 'size',
                'clear': 'clear',
                'remove': 'erase',
                'isEmpty': 'empty'
            },
            'std::unordered_set': {
                'add': 'insert',
                'contains': 'find',
                'remove': 'erase',
                'size': 'size',
                'clear': 'clear',
                'isEmpty': 'empty'
            },
            'std::unordered_map': {
                'put': 'insert',
                'get': 'at',
                'containsKey': 'find',
                'remove': 'erase',
                'size': 'size',
                'clear': 'clear',
                'isEmpty': 'empty'
            }
        }
        self.current_access = None

    def indent_str(self) -> str:
        return "    " * self.current_indent

    def add_include(self, header: str):
        self.required_includes.add(f"#include <{header}>")

    def get_result(self) -> str:
        result = []
        result.extend(sorted(self.required_includes))
        if self.required_includes:
            result.append("")
        result.extend(self.output)
        return '\n'.join(result)

    def translate_type(self, java_type: str) -> str:
        type_mapping = {
            'String': 'std::string',
            'Integer': 'int',
            'Boolean': 'bool',
            'boolean': 'bool',
            'Float': 'float',
            'float': 'float',
            'int': 'int',
            'void': 'void',
            'double': 'double',
            'Double': 'double',
            'List': 'std::vector',
            'ArrayList': 'std::vector',
            'Map': 'std::map',
            'HashMap': 'std::unordered_map',
            'Set': 'std::set',
            'HashSet': 'std::unordered_set'
        }

        to_remove = None
        for key in self.includes:
            if key in java_type:
                self.add_include(self.includes[key])
                to_remove = key
        if to_remove:
            self.includes.pop(to_remove)

        if '<' in java_type:
            base_type = java_type[:java_type.index('<')]
            generics = java_type[java_type.index('<') + 1:java_type.rindex('>')]

            translated_base = type_mapping.get(base_type, base_type)

            generic_params = []
            depth = 0
            current = ""
            for char in generics:
                if char == '<':
                    depth += 1
                elif char == '>':
                    depth -= 1
                elif char == ',' and depth == 0:
                    generic_params.append(self.translate_type(current.strip()))
                    current = ""
                    continue
                current += char
            if current:
                generic_params.append(self.translate_type(current.strip()))

            return f"{translated_base}<{', '.join(generic_params)}>"

        return type_mapping.get(java_type, java_type)

    def get_collection_type(self, java_type: str) -> str:
        collection_mapping = {
            'List': 'std::vector',
            'ArrayList': 'std::vector',
            'Set': 'std::unordered_set',
            'HashSet': 'std::unordered_set',
            'Map': 'std::unordered_map',
            'HashMap': 'std::unordered_map'
        }
        if java_type in collection_mapping:
            self.add_include(self.includes[java_type])
            return collection_mapping[java_type]
        return java_type

    def extract_modifiers(self, ctx) -> str:
        if not hasattr(ctx, 'parentCtx') or not ctx.parentCtx:
            return "private"

        parent = ctx.parentCtx
        if not hasattr(parent, 'modifier') or not parent.modifier():
            return "private"

        modifiers = parent.modifier()
        if not modifiers:
            return "private"

        if not isinstance(modifiers, list):
            modifiers = [modifiers]

        for mod in modifiers:
            if mod.PUBLIC():
                return "public"
            elif mod.PRIVATE():
                return "private"
            elif mod.PROTECTED():
                return "protected"

        return "private"

    def visit_CompilationUnitContext(self, ctx):
        for child in ctx.typeDeclaration():
            self.visit(child)
        return self.get_result()

    def visit_TypeDeclarationContext(self, ctx):
        if ctx.classDeclaration():
            return self.visit(ctx.classDeclaration())
        return ""

    def visit_ClassDeclarationContext(self, ctx):
        class_name = ctx.Identifier().getText()
        self.current_class = class_name
        self.class_fields = {}
        self.current_access = None

        self.output.append(f"class {class_name} {{")
        self.current_indent += 1

        self.constructor_fields = {}

        if ctx.classBody():
            for decl in ctx.classBody().classBodyDeclaration():
                if hasattr(decl, 'memberDeclaration') and decl.memberDeclaration():
                    member = decl.memberDeclaration()
                    self.visit_member(member)

        self.current_indent -= 1
        self.output.append("};")
        self.output.append("")
        self.current_class = None
        return ""

    def visit_member(self, member):
        access = self.extract_modifiers(member)

        if access != self.current_access:
            if self.current_access is not None:
                self.output.append("")
            self.output.append(f"{access}:")
            self.current_access = access

        if hasattr(member, 'fieldDeclaration') and member.fieldDeclaration():
            self.visit_FieldDeclarationContext(member.fieldDeclaration())

        elif hasattr(member, 'methodDeclaration') and member.methodDeclaration():
            self.visit_MethodDeclarationContext(member.methodDeclaration())

        elif hasattr(member, 'constructorDeclaration') and member.constructorDeclaration():
            self.visit_ConstructorDeclarationContext(member.constructorDeclaration())


    def visit_FieldDeclarationContext(self, ctx):
        if ctx is None or not hasattr(ctx, 'typeRule') or ctx.typeRule() is None:
            return ""

        field_type = self.translate_type(ctx.typeRule().getText())

        if not hasattr(ctx, 'variableDeclarators') or ctx.variableDeclarators() is None:
            return ""

        for var_decl in ctx.variableDeclarators().variableDeclarator():
            if var_decl is None or not hasattr(var_decl, 'variableDeclaratorId'):
                continue

            var_name = var_decl.variableDeclaratorId().getText()
            self.class_fields[var_name] = field_type

            initializer = ""
            if hasattr(var_decl, 'variableInitializer') and var_decl.variableInitializer():
                init_expr = var_decl.variableInitializer().getText()
                initializer = f" = {init_expr}"

            self.output.append(f"{self.indent_str()}{field_type} {var_name}{initializer};")
        return ""

    def visit_MethodDeclarationContext(self, ctx):
        method_name = ctx.Identifier().getText()
        return_type = "void"
        if ctx.typeRule():
            return_type = self.translate_type(ctx.typeRule().getText())
        params = self.visit(ctx.formalParameters())
        param_str = ", ".join(params) if params else ""

        self.output.append(f"{self.indent_str()}{return_type} {method_name}({param_str}) {{")
        if ctx.methodBody() and ctx.methodBody().block():
            self.current_indent += 1
            self.visit(ctx.methodBody().block())
            self.current_indent -= 1
        self.output.append(f"{self.indent_str()}}}")
        self.output.append("")
        return ""

    def visit_ConstructorDeclarationContext(self, ctx):
        constructor_name = ctx.Identifier().getText()
        params = []
        param_names = []
        field_inits = []

        if hasattr(ctx, 'formalParameters') and ctx.formalParameters():
            params = self.visit(ctx.formalParameters())
            formal_param_list = ctx.formalParameters().formalParameterList()
            if formal_param_list:
                for param in formal_param_list.formalParameter():
                    param_names.append(param.variableDeclaratorId().getText())

        param_str = ", ".join(params) if params else ""

        if hasattr(ctx, 'constructorBody') and ctx.constructorBody():
            constructor_body = ctx.constructorBody()
            if hasattr(constructor_body, 'blockStatement'):
                for stmt in constructor_body.blockStatement():
                    if self._is_field_init(stmt):
                        field_name, value = self._get_field_init_info(stmt)
                        if value in param_names:
                            field_inits.append(f"{field_name}({value})")
                        else:
                            field_inits.append(f"{field_name}({value})")

        for field_name, field_type in self.class_fields.items():
            if not any(field_name in init for init in field_inits):
                if field_type == "int":
                    field_inits.append(f"{field_name}(0)")
                elif field_type == "double":
                    field_inits.append(f"{field_name}(0.0)")
                elif field_type == "bool":
                    field_inits.append(f"{field_name}(false)")
                elif field_type == "std::string":
                    field_inits.append(f'{field_name}("")')

        if field_inits:
            init_list = " : " + ", ".join(field_inits)
            self.output.append(f"{self.indent_str()}{constructor_name}({param_str}){init_list} {{")
        else:
            self.output.append(f"{self.indent_str()}{constructor_name}({param_str}) {{")

        if ctx.constructorBody():
            self.current_indent += 1
            for stmt in ctx.constructorBody().blockStatement():
                if not self._is_field_init(stmt):
                    self.visit(stmt)
            self.current_indent -= 1

        self.output.append(f"{self.indent_str()}}}")
        self.output.append("")
        return ""

    def visit_FormalParametersContext(self, ctx):
        params = []
        if hasattr(ctx, 'formalParameterList') and ctx.formalParameterList():
            for param in ctx.formalParameterList().formalParameter():
                param_type = self.translate_type(param.typeRule().getText())
                param_name = param.variableDeclaratorId().getText()
                params.append(f"{param_type} {param_name}")
        return params

    def visit_BlockContext(self, ctx):
        for child in ctx.children:
            if hasattr(child, 'COMMENT'):
                comment = child.getText()
                self.output.append(f"{self.indent_str()}{comment}")
            else:
                self.visit(child)

    def visit_BlockStatementContext(self, ctx):
        if hasattr(ctx, 'COMMENT'):
            comment = ctx.getText()
            self.output.append(f"{self.indent_str()}{comment}")
            return ""

        if ctx.statement():
            statement = ctx.statement()

            if hasattr(statement, 'statementExpression'):
                expr = statement.statementExpression().getText()
                if "this." in expr:
                    expr = expr.replace("this.", "this->")
                    self.output.append(f"{self.indent_str()}{expr};")
                    return ""

            if hasattr(statement, 'FOR') and statement.FOR():
                for_control = statement.forControl()

                init = ""
                if for_control.forInit():
                    if hasattr(for_control.forInit(), 'localVariableDeclaration'):
                        init_decl = for_control.forInit().localVariableDeclaration()
                        var_type = self.translate_type(init_decl.typeRule().getText())
                        var_decl = init_decl.variableDeclarators().variableDeclarator()[0]
                        var_name = var_decl.variableDeclaratorId().getText()
                        init_value = ""
                        if hasattr(var_decl, 'variableInitializer') and var_decl.variableInitializer():
                            init_value = var_decl.variableInitializer().getText()
                        init = f"{var_type} {var_name}{{{init_value}}}"
                    else:
                        init = for_control.forInit().getText()

                condition = for_control.expression().getText() if for_control.expression() else ""
                update = for_control.forUpdate().getText() if for_control.forUpdate() else ""

                self.output.append(f"{self.indent_str()}for ({init}; {condition}; {update}) {{")
                self.current_indent += 1
                if statement.statement():
                    if hasattr(statement.statement(), 'block'):
                        self.visit(statement.statement().block())
                    else:
                        result = self.visit(statement.statement())
                        if result:
                            self.output.append(f"{self.indent_str()}{result}")
                self.current_indent -= 1
                self.output.append(f"{self.indent_str()}}}")
                self.output.append("")
                return ""

            elif hasattr(statement, 'IF') and statement.IF():
                condition = statement.parExpression().expression().getText()

                self.output.append(f"{self.indent_str()}if ({condition}) {{")
                self.current_indent += 1

                if_statement = statement.statement(0)
                if hasattr(if_statement, 'block'):
                    self.visit(if_statement.block())
                else:
                    result = self.visit(if_statement)
                    if result:
                        self.output.append(f"{self.indent_str()}{result}")

                self.current_indent -= 1
                self.output.append(f"{self.indent_str()}}}")

                if hasattr(statement, 'ELSE') and statement.ELSE():
                    else_statement = statement.statement(1)
                    self.output.append(f"{self.indent_str()}else {{")
                    self.current_indent += 1

                    if hasattr(else_statement, 'block'):
                        self.visit(else_statement.block())
                    else:
                        result = self.visit(else_statement)
                        if result:
                            self.output.append(f"{self.indent_str()}{result}")

                    self.current_indent -= 1
                    self.output.append(f"{self.indent_str()}}}")

                self.output.append("")
                return ""

            if hasattr(statement, 'WHILE') and statement.WHILE():
                condition = statement.parExpression().expression().getText()
                self.output.append(f"{self.indent_str()}while ({condition}) {{")
                self.current_indent += 1

                while_statement = statement.statement()
                if hasattr(while_statement, 'block'):
                    for blockStmt in while_statement.block().getChildren():
                        if not hasattr(blockStmt, 'LBRACE') and not hasattr(blockStmt, 'RBRACE'):
                            self.visit(blockStmt)
                else:
                    if hasattr(while_statement, 'statementExpression'):
                        expr = while_statement.statementExpression().expression().getText()
                        self.output.append(f"{self.indent_str()}{expr};")
                    else:
                        stmt_expr = while_statement.statementExpression()
                        if stmt_expr:
                            expr = stmt_expr.getText()
                            self.output.append(f"{self.indent_str()}{expr};")
                        else:
                            result = self.visit(while_statement)
                            if result:
                                self.output.append(f"{self.indent_str()}{result}")

                self.current_indent -= 1
                self.output.append(f"{self.indent_str()}}}")
                self.output.append("")
                return ""

            else:
                return self.visit(statement)

        elif ctx.localVariableDeclaration():
            return self.visit_LocalVariableDeclarationContext(ctx.localVariableDeclaration())

        return ""

    def visit_StatementContext(self, ctx):
        if ctx.RETURN():
            if ctx.expression():
                expr = self.translate_expression(ctx.expression())
                return f"return {expr};"
            return "return;"
        elif ctx.printlnStatement():
            if ctx.printlnStatement().expressionList():
                expressions = [expr.getText() for expr in ctx.printlnStatement().expressionList().expression()]
                return f"std::cout << {' << '.join(expressions)} << std::endl;"
            return "std::cout << std::endl;"
        elif ctx.statementExpression():
            return f"{ctx.statementExpression().getText()};"

        return ""

    def translate_expression(self, expr):
        if expr is None:
            return ""

        if expr.getChildCount() == 3:
            operator = expr.getChild(1).getText()
            left = self.translate_expression(expr.getChild(0))
            right = self.translate_expression(expr.getChild(2))
            return f"{left} {operator} {right}"

        if expr.getChildCount() == 1:
            if hasattr(expr, 'getText'):
                text = expr.getText()
                if text == "System.out.println":
                    return "std::cout"
                return text

        if hasattr(expr, 'methodInvocation'):
            obj = expr.getChild(0).getText()
            method = expr.getChild(1).getText()
            args = self.translate_expression(expr.getChild(2)) if expr.getChildCount() > 2 else ""

            if obj == "System.out" and method == "println":
                args = args.replace(" + ", " << ")
                return f"std::cout << {args} << std::endl"
            return f"{obj}.{method}({args})"

        return expr.getText() if hasattr(expr, 'getText') else ""

    def translate_method_call(self, obj_name, method_name, args):
        object_type = None
        if obj_name in self.local_variables:
            object_type = self.local_variables[obj_name]
        elif obj_name in self.class_fields:
            object_type = self.class_fields[obj_name]

        if obj_name == "System.out" and method_name == "println":
            if args:
                return f"std::cout << {args} << std::endl"
            return "std::cout << std::endl"

        if object_type in self.collection_methods:
            cpp_methods = self.collection_methods[object_type]
            if method_name in cpp_methods:
                cpp_method = cpp_methods[method_name]

                if object_type == 'std::unordered_map' and method_name == 'put':
                    key, value = args.split(',', 1)
                    return f"{obj_name}.insert({{{key.strip()}, {value.strip()}}})"

                if object_type == 'std::unordered_set' and method_name == 'contains':
                    return f"{obj_name}.find({args}) != {obj_name}.end()"

                if object_type == 'std::unordered_map' and method_name == 'containsKey':
                    return f"{obj_name}.find({args}) != {obj_name}.end()"

                return f"{obj_name}.{cpp_method}({args})"

        return f"{obj_name}.{method_name}({args})"

    def visit_MethodCallExprContext(self, ctx):
        obj = ctx.expression().getText()
        method = ctx.methodInvocation().Identifier().getText()
        args = ""

        if ctx.methodInvocation().expressionList():
            args = ", ".join(
                self.translate_expression(expr) for expr in ctx.methodInvocation().expressionList().expression())

        translated_call = self.translate_method_call(obj, method, args)
        self.output.append(f"{self.indent_str()}{translated_call};")
        return ""

    def visit_LocalVariableDeclarationContext(self, ctx):
        if ctx is None:
            return ""

        var_type = self.translate_type(ctx.typeRule().getText())
        original_type = ctx.typeRule().getText()

        for var_decl in ctx.variableDeclarators().variableDeclarator():
            var_name = var_decl.variableDeclaratorId().getText()

            if 'ArrayList' in original_type or 'List' in original_type:
                self.local_variables[var_name] = 'std::vector'
            elif 'HashSet' in original_type:
                self.local_variables[var_name] = 'std::unordered_set'
            elif 'HashMap' in original_type:
                self.local_variables[var_name] = 'std::unordered_map'
            else:
                self.local_variables[var_name] = var_type

            if hasattr(var_decl, 'variableInitializer') and var_decl.variableInitializer():
                init_value = var_decl.variableInitializer().getText()
                if 'newArrayList' in init_value or 'newHashSet' in init_value or 'newHashMap' in init_value:
                    self.output.append(f"{self.indent_str()}{var_type} {var_name}{{}};")
                elif var_type == "std::string":
                    self.output.append(f"{self.indent_str()}{var_type} {var_name}{{{init_value}}};")
                else:
                    if var_type == "std::string" and init_value.startswith('"'):
                        init_value = init_value.strip('"')
                    self.output.append(f"{self.indent_str()}{var_type} {var_name}{{{init_value}}};")
            else:
                self.output.append(f"{self.indent_str()}{var_type} {var_name}{{}};")
        return ""

    def visit_PrintlnStatementContext(self, ctx):
        if hasattr(ctx, 'expressionList') and ctx.expressionList():
            expressions = []
            for expr in ctx.expressionList().expression():
                text = expr.getText()
                if '+' in text:
                    parts = text.split('+')
                    expressions.extend(part.strip() for part in parts)
                else:
                    expressions.append(text)
            self.output.append(f"{self.indent_str()}std::cout << {' << '.join(expressions)} << std::endl;")
        else:
            self.output.append(f"{self.indent_str()}std::cout << std::endl;")
        return ""

    def visit_ReturnStmtContext(self, ctx):
        if ctx.expression():
            expr = ctx.expression().getText()
            self.output.append(f"{self.indent_str()}return {expr};")
        else:
            self.output.append(f"{self.indent_str()}return;")
        return ""

    def _is_field_init(self, stmt) -> bool:
        if (hasattr(stmt, 'statement') and
                hasattr(stmt.statement(), 'statementExpression') and
                stmt.statement().statementExpression()):
            expr = stmt.statement().statementExpression().expression()
            if expr and expr.getText().startswith('this.'):
                field_name = expr.getText().split('.')[1].split('=')[0]
                return field_name in self.class_fields
        return False

    def _get_field_init_info(self, stmt):
        expr = stmt.statement().statementExpression().expression()
        field_name = expr.getText().split('.')[1].split('=')[0]
        value = expr.getText().split('=')[1].strip()
        return field_name, value

    def save_parse_tree_pretty(self, tree: ParserRuleContext, parser: Parser, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            self._write_tree(node=tree, parser=parser, file=f, indent=0)

    def _write_tree(self, node: ParserRuleContext, parser: Parser, file, indent: int):
        indentation = "  " * indent
        rule_name = parser.ruleNames[node.getRuleIndex()]
        node_text = node.getText().replace('\n', '\\n')
        file.write(f"{indentation}{rule_name}: {node_text}\n")
        for child in node.getChildren():
            if isinstance(child, ParserRuleContext):
                self._write_tree(child, parser, file, indent + 1)


def translate_java_to_cpp(java_code: str) -> str:
    input_stream = InputStream(java_code)
    lexer = JavaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JavaGrammar(stream)
    tree = parser.compilationUnit()

    translator = JavaToCppTranslator()
    result = translator.visit(tree)
    translator.save_parse_tree_pretty(tree, parser, "parse_tree.txt")
    return result


def translate_file(input_path: str, output_path: str) -> bool:
    try:
        with open(input_path, 'r', encoding='utf-8') as inf:
            code = inf.read()
        print(f"Translating {input_path} to {output_path}...")
        result = translate_java_to_cpp(code)
        print("Generated output:")
        print(result)

        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as outf:
            outf.write(result)

        print(f"Successfully translated {input_path} to {output_path}.")
        return True
    except Exception as e:
        print(f"Error during translation: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False
