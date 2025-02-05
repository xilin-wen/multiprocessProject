import pymysql  # 导入 pymysql 以操作 MySQL 数据库
from pymysql.cursors import DictCursor  # 使用 DictCursor 以字典形式返回查询结果
from typing import Any, List, Dict, Optional  # 引入类型提示


class MySQLClient:
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3303):
        # 初始化 MySQL 连接参数
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = self._connect()  # 建立数据库连接

    def _connect(self):
        # 连接 MySQL 数据库
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
            cursorclass=DictCursor,  # 以字典形式返回数据
            autocommit=False  # 禁用自动提交，以便进行事务控制
        )

    def execute(self, query: str, params: Optional[List[Any]] = None) -> int:
        """执行 INSERT、UPDATE、DELETE 语句，返回影响的行数"""
        with self.conn.cursor() as cursor:  # 获取数据库游标
            cursor.execute(query, params or [])  # 执行 SQL 语句
            self.conn.commit()  # 提交事务
            return cursor.rowcount  # 返回影响的行数

    def fetch_one(self, query: str, params: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        """执行 SELECT 语句，返回一行结果"""
        with self.conn.cursor() as cursor:  # 获取数据库游标
            cursor.execute(query, params or [])  # 执行 SQL 查询
            return cursor.fetchone()  # 返回查询到的第一行数据

    def fetch_all(self, query: str, params: Optional[List[Any]] = None) -> tuple[tuple[Any, ...], ...]:
        """执行 SELECT 语句，返回所有结果"""
        with self.conn.cursor() as cursor:  # 获取数据库游标
            cursor.execute(query, params or [])  # 执行 SQL 查询
            return cursor.fetchall()  # 返回所有查询结果

    def execute_many(self, query: str, params: List[List[Any]]) -> int:
        """批量执行 SQL 语句"""
        with self.conn.cursor() as cursor:  # 获取数据库游标
            cursor.executemany(query, params)  # 批量执行 SQL 语句
            self.conn.commit()  # 提交事务
            return cursor.rowcount  # 返回影响的行数

    def transaction(self, queries: List[str], params_list: List[List[Any]]) -> bool:
        """执行事务，保证多个 SQL 语句要么全部执行，要么全部回滚"""
        if len(queries) != len(params_list):
            raise ValueError("查询语句和参数列表的数量不匹配。")

        try:
            # 禁用自动提交
            self.conn.autocommit = False

            with self.conn.cursor() as cursor:  # 获取数据库游标
                for query, params in zip(queries, params_list):  # 遍历所有 SQL 语句
                    print(f"正在执行查询语句: {query}，参数为：{params}")
                    cursor.execute(query, params)  # 执行 SQL 语句

            # 在所有语句成功执行后提交事务
            self.conn.commit()
            print("事务执行成功")
            return True  # 事务执行成功
        except pymysql.MySQLError as e:
            # 仅捕获与 MySQL 相关的错误并回滚
            self.conn.rollback()  # 发生异常时回滚事务
            print(f"事务执行失败，错误为: {e}")  # 打印错误信息
            return False  # 返回 False 表示事务失败
        except Exception as e:
            # 其他异常处理
            self.conn.rollback()  # 发生异常时回滚事务
            print(f"异常错误: {e}")
            return False
        finally:
            # 恢复自动提交状态
            self.conn.autocommit = True

    def create_table(self, table: str, columns: Dict[str, str], primary_key: Optional[str] = None) -> None:
        """创建表"""
        column_definitions = [f"{col} {dtype}" for col, dtype in columns.items()]
        if primary_key:
            column_definitions.append(f"主键：({primary_key})")
        query = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(column_definitions)})"
        self.execute(query)

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """执行 INSERT 语句"""
        keys = ", ".join(data.keys())
        values = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({keys}) VALUES ({values})"

        with self.conn.cursor() as cursor:
            cursor.execute(query, list(data.values()))
            return cursor.rowcount  # 返回受影响行数

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """执行 UPDATE 语句"""
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        where_clause = " AND ".join([f"{k} = %s" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        with self.conn.cursor() as cursor:
            cursor.execute(query, list(data.values()) + list(where.values()))
            return cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """执行 DELETE 语句"""
        where_clause = " AND ".join([f"{k} = %s" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"

        with self.conn.cursor() as cursor:
            cursor.execute(query, list(where.values()))
            return cursor.rowcount

    def select(self, table: str, where: Optional[Dict[str, Any]] = None, columns: Optional[List[str]] = None) -> tuple[
        tuple[Any, ...], ...]:
        """查询数据"""
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"
        params = []
        if where:
            where_clause = " AND ".join([f"{key} = %s" for key in where.keys()])
            query += f" WHERE {where_clause}"
            params = list(where.values())
        return self.fetch_all(query, params)

    def transactionFunc(self, operations: List[Dict[str, Any]]) -> bool:
        """
        事务执行函数：确保所有操作要么全部成功，要么全部失败回滚。
        operations: List[Dict]
        - "action": insert/update/delete/select
        - "table": 目标表名
        - "data": 数据（用于 insert/update）
        - "where": 过滤条件（用于 update/delete/select）
        """
        try:
            self.conn.autocommit = False  # 关闭自动提交，确保事务生效
            with self.conn.cursor() as cursor:
                for op in operations:
                    action = op["action"]
                    table = op["table"]
                    data = op.get("data", {})
                    where = op.get("where", {})

                    if action == "insert":
                        self.insert(table, data)  # 插入操作
                    elif action == "update":
                        self.update(table, data, where)  # 更新操作
                    elif action == "delete":
                        affected_rows = self.delete(table, where)  # 删除操作
                        if affected_rows == 0:
                            raise ValueError(f"删除失败：参数 {where} 所在行不存在")  # 触发回滚
                    elif action == "select":
                        print(self.select(table, where))  # 查询操作
                    else:
                        raise ValueError(f"不支持的操作: {action}")

            self.conn.commit()  # 事务提交
            print("事务执行成功")
            return True
        except Exception as e:
            self.conn.rollback()  # 发生错误时回滚
            print(f"事务执行失败，错误为: {e}")  # 打印错误信息
            return False
        finally:
            self.conn.autocommit = True  # 恢复自动提交状态

    def close(self):
        """关闭数据库连接"""
        self.conn.close()  # 关闭 MySQL 连接


# 测试代码
if __name__ == "__main__":
    db = MySQLClient(host="localhost", user="xilin", password="123456", database="test")

    # **创建表**
    # db.create_table("users2", {
    #     "id": "INT AUTO_INCREMENT",
    #     "name": "VARCHAR(100) NOT NULL",
    #     "age": "INT",
    # }, primary_key="id")

    # 插入数据
    # db.insert("users2", {"name": "David", "age": 40})

    # 查询数据
    # print(db.select("users2"))

    # 更新数据
    # db.update("users2", {"age": 41}, {"name": "David"})

    # # 删除数据
    # db.delete("users2", {"name": "David"})

    # transaction_success = db.transactionFunc([
    #     {"action": "insert", "table": "users2", "data": {"name": "Alice", "age": 30}},
    #     # {"action": "insert", "table": "users2", "data": {"name": "Bob", "age": 25}},
    #     {"action": "update", "table": "users2", "data": {"age": 35}, "where": {"name": "Alice"}},
    #     {"action": "delete", "table": "users2", "where": {"name": "Bob"}}
    # ])

    # 插入单条数据
    # db.execute("INSERT INTO users2 (name, age) VALUES (%s, %s)", ["Alice", 25])

    # 批量插入数据
    # db.execute_many("INSERT INTO users2 (name, age) VALUES (%s, %s)", [["Bob", 30], ["Charlie", 35]])

    # # 查询单条数据
    # print("Single Fetch:", db.fetch_one("SELECT * FROM users2 WHERE name=%s", ["Alice"]))

    # # 查询所有数据
    # print("All Fetch:", db.fetch_all("SELECT * FROM users2"))

    # # 事务测试，包含故意的 SQL 语法错误，检查事务回滚
    # success = db.transaction([
    #     "INSERT INTO users2 (name, age) VALUES (%s, %s)",  # 插入一条新数据
    #     "UPDATE users2 SET age = age + 1 WHERE name = %s",  # 更新用户年龄
    #     "INVALID SQL"  # 故意制造的 SQL 语法错误
    # ], [["David", 40], ["Alice"]])  # 最后一个 SQL 语句错误，应触发回滚
    # #
    # print("Transaction Success:", success)  # 输出事务执行结果
    # print("All Fetch After Transaction:", db.fetch_all("SELECT * FROM users2"))  # 确保数据未修改

    db.close()  # 关闭数据库连接