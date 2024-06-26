import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3

# プルダウンリストの中身
EVALUATION_VALUE = (" - ", " ★☆☆☆☆ ", " ★★☆☆☆ ",
                    " ★★★☆☆ ", " ★★★★☆ ", " ★★★★★ ")
STATUS_VALUE = ("0:欲しい", "1:購入済、未読", "2:読書中", "3:読了", "4:途中放棄")


"""
メインウィンドウクラス
"""
class MainWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("Dokusyo App")

        # データベースとの接続
        self.db = DatabaseSession()

        # Bookのインスタンス化
        self.book = Book()

        # ウィンドウを閉じられた時に処理を実行
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)

        # ウィジェットの配置
        self.set_widget()

    def close_window(self):
        self.db.disconnect()
        self.master.destroy()

    def set_widget(self):
        # ********* 1行目 ************
        # アプリタイトル
        label_title = ttk.Label(self.master, text="読書管理アプリ", anchor=tk.CENTER)
        label_title.grid(row=0, column=0, columnspan=3, ipadx=20, ipady=5, pady=10)
        # ********* 2行目 *************
        # 追加ボタン
        btn_add = ttk.Button(self.master, text="追加", command=self.add)
        btn_add.grid(row=1, column=0)
        # 更新ボタン
        btn_update = ttk.Button(self.master, text="更新", command=self.update)
        btn_update.grid(row=1, column=1)
        # 削除ボタン
        btn_delete = ttk.Button(self.master, text="削除", command=self.delete)
        btn_delete.grid(row=1, column=2)
        # ********* 3行目 ************
        # フレーム
        frame = ttk.Frame(self.master, width=700, height=200)
        frame.grid_propagate(False)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, ipadx=5, ipady=5)
        # ********** 表領域 ***********
        # 表
        column = ("id", "name", "auther", "evaluation",
                  "status", "purchasedate", "startdate", "enddate", "pages", "url", "comment")
        self.table_books = ttk.Treeview(frame, columns=column, height=10, selectmode="browse", show="headings")
        self.table_books.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.table_books.bind("<<TreeviewSelect>>", self.select_record)

        # 列の設定(P29)
        self.table_books.column("id", anchor="center", width=30, stretch=False)
        self.table_books.column("name", anchor="w", width=300, stretch=False)
        self.table_books.column("auther", anchor="w", width=100, stretch=False)
        self.table_books.column("evaluation", anchor="center", width=100, stretch=False)
        self.table_books.column("status", anchor="center", width=100, stretch=False)
        self.table_books.column("purchasedate", anchor="center", width=80, stretch=False)
        self.table_books.column("startdate", anchor="center", width=80, stretch=False)
        self.table_books.column("enddate", anchor="center", width=80, stretch=False)
        self.table_books.column("pages", anchor="e", width=60, stretch=False)
        self.table_books.column("url", anchor="w", width=300, stretch=False)
        self.table_books.column("comment", anchor="w", width=300, stretch=False)
        
        # ヘッダ行の設定
        self.table_books.heading("id", text="#", anchor="center")
        self.table_books.heading("name", text="書籍名", anchor="center")
        self.table_books.heading("auther", text="著者", anchor="center")
        self.table_books.heading("evaluation", text="評価", anchor="center")
        self.table_books.heading("status", text="ステータス", anchor="center")
        self.table_books.heading("purchasedate", text="購入日", anchor="center")
        self.table_books.heading("startdate", text="開始日", anchor="center")
        self.table_books.heading("enddate", text="読了日", anchor="center")
        self.table_books.heading("pages", text="ページ数", anchor="center")
        self.table_books.heading("url", text="URL", anchor="center")
        self.table_books.heading("comment", text="コメント", anchor="center")

        self.display_list()

        # 縦スクロールバー
        vscrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        vscrollbar.config(command=self.table_books.yview)
        vscrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.table_books.config(yscrollcommand=vscrollbar.set)
        # 横スクロールバー
        hscrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        hscrollbar.config(command=self.table_books.xview)
        hscrollbar.grid(row=1, column=0, sticky=tk.EW)
        self.table_books.config(xscrollcommand=hscrollbar.set)

        # スタイルの適用
        style = ttk.Style()
        style.theme_use("clam")

    def add(self):
        sub_window = SubWindow(self, "add")

    def update(self):
        # リストが選択されている場合にサブウィンドウを表示
        if self.id != -1:
            sub_window = SubWindow(self, "update")

    def delete(self):
        # リストが選択されている場合にサブウィンドウを表示
        if self.id != -1:
            ret = messagebox.askyesno("削除確認", "削除していいですか？")
            if ret:
                # 「はい」が押されていたら削除
                self.book.delete(self.db, self.id)
                # リストを再描画
                self.display_list()

    def select_record(self, e):
        # 選択行の取得
        select_id = self.table_books.focus()
        if select_id != "":
            # 選択行のレコードの値を取得
            values = self.table_books.item(select_id, "values")
            self.id = values[0]
    
    def display_list(self):
        # 既存レコードの削除
        for row in self.table_books.get_children():
            self.table_books.delete(row)
    
        # 検索
        books = self.book.select_all(self.db)

        # レコードの追加
        for index, book in enumerate(books):
            self.table_books.insert(
                parent="", index="end", iid=index,
                values=(book.id,
                        book.name,
                        book.auther,
                        book.evaluation,
                        book.status,
                        book.purchase_date,
                        book.start_date,
                        book.end_date,
                        book.pages,
                        book.url,
                        book.comment)
            )
        # リスト選択のID値を初期化（未選択状態）
        self.id = -1

        # 再描画
        self.master.update()

"""
サブウィンドウクラス
"""
class SubWindow:
    def __init__(self, master, mode) -> None:
        # パラメータの受け取り
        self.master = master
        self.mode = mode
        self.db = master.db
        self.id = master.id
        self.book = master.book

        # サブウィンドウの描画
        self.sub_window = tk.Toplevel()
        self.sub_window.title("Description")
        self.sub_window.grab_set()

        if mode == "add":
            self.book_info = Book()
        else:
            self.book_info = self.book.select(self.db, self.id)
        # 全ウィジェットの配置
        self.set_widget()

        # ウィンドウを閉じられた時に処理を実行
        self.sub_window.protocol("WM_DELETE_WINDOW", self.close_window)
    
    def close_window(self):
        # リストの再描画
        self.master.display_list()

        # サブウィンドウを閉じる
        self.sub_window.destroy()

    def set_widget(self):
        # ********* 1行目 *********
        # 書籍名ラベル
        label_book_title = ttk.Label(self.sub_window, text="書籍名：")
        label_book_title.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        # 書籍名入力欄
        self.str_book_title = tk.StringVar()
        text_book_title = ttk.Entry(self.sub_window, width=50)
        text_book_title.grid(row=0, column=1, columnspan=2, sticky=tk.W)
        text_book_title.config(textvariable=self.str_book_title)
        self.str_book_title.set(self.book_info.name)
        # 著者ラベル
        label_author = ttk.Label(self.sub_window, text="業者：")
        label_author.grid(row=0, column=3, padx=5, pady=5, sticky=tk.E)
        # 著者入力欄
        self.str_auther = tk.StringVar()
        text_author = ttk.Entry(self.sub_window, width=20)
        text_author.grid(row=0, column=4, columnspan=2, sticky=tk.W)
        text_author.config(textvariable=self.str_auther)
        self.str_auther.set(self.book_info.auther)

        # ********* 2行目 ********
        # 評価ラベル
        label_evaluation = ttk.Label(self.sub_window, text="評価：")
        label_evaluation.grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        # 評価ドロップダウンリスト
        self.str_evaluation = tk.StringVar()
        combo_evaluation = ttk.Combobox(self.sub_window, values=EVALUATION_VALUE, state="readonly")
        combo_evaluation.grid(row=1, column=1, columnspan=2, sticky=tk.W)
        combo_evaluation.config(textvariable=self.str_evaluation)
        self.str_evaluation.set(self.book_info.evaluation)

        # ステータスラベル
        label_status = ttk.Label(self.sub_window, text="ステータス：")
        label_status.grid(row=1, column=3, padx=5, pady=5, sticky=tk.E)
        # ステータスドロップダウンリスト
        self.str_status = tk.StringVar()
        combo_status = ttk.Combobox(self.sub_window, values=STATUS_VALUE, state="readonly")
        combo_status.grid(row=1, column=4, columnspan=2, sticky=tk.W)
        combo_status.config(textvariable=self.str_status)
        combo_status.set(self.book_info.status)

        # ********** 3行目 *********
        # 購入日ラベル
        label_purchase_date = ttk.Label(self.sub_window, text="購入日：")
        label_purchase_date.grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        # 購入日カレンダー
        self.str_purchase_date = tk.StringVar()
        self.date_purchase = DateEntry(self.sub_window, showweekbumber=False)
        self.date_purchase.grid(row=2, column=1, sticky=tk.W)
        self.date_purchase.config(textvariable=self.str_purchase_date)
        self.str_purchase_date.set(self.book_info.purchase_date)
        # 購入日クリアボタン
        btn_clear_purchase = ttk.Button(self.sub_window, text="<-Clear")
        btn_clear_purchase.grid(row=2, column=2, sticky=tk.W)
        btn_clear_purchase.config(command=lambda:self.date_purchase.delete(0, "end"))
        # 開始日ラベル
        label_start_date = ttk.Label(self.sub_window, text="開始日：")
        label_start_date.grid(row=2, column=3, padx=5, sticky=tk.E)
        # 開始日カレンダ
        self.str_start_date = tk.StringVar()
        self.date_start = DateEntry(self.sub_window, showweeknumbers=False)
        self.date_start.grid(row=2, column=4, sticky=tk.W)
        self.date_start.config(textvariable=self.str_start_date)
        self.str_start_date.set(self.book_info.start_date)
        # 開始日クリアボタン
        btn_clear_start = ttk.Button(self.sub_window, text="<-Clear")
        btn_clear_start.grid(row=2, column=5, sticky=tk.W)
        btn_clear_start.config(command=lambda:self.date_start.delete(0, "end"))
        
        # ********** 4行目 ********
        # 読了日ラベル
        label_finish_date = ttk.Label(self.sub_window, text="読了日：")
        label_finish_date.grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        # 読了日カレンダ
        self.str_end_date = tk.StringVar()
        self.date_end = DateEntry(self.sub_window, showweeknumbers=False)
        self.date_end.grid(row=3, column=1, sticky=tk.W)
        self.date_end.config(textvariable=self.str_end_date)
        self.str_end_date.set(self.book_info.end_date)
        # 読了日クリアボタン
        btn_clear_end = ttk.Button(self.sub_window, text="<-Clear")
        btn_clear_end.grid(row=3, column=2, sticky=tk.W)
        btn_clear_end.config(command=lambda:self.date_end.delete(0, "end"))
        # 総ページ数ラベル
        label_total_page = ttk.Label(self.sub_window, text="総ページ数：")
        label_total_page.grid(row=3, column=3, padx=5, sticky=tk.E)
        # 総ページ数入力欄
        self.str_pages = tk.StringVar()
        text_total_page = ttk.Entry(self.sub_window, width=10)
        text_total_page.grid(row=3, column=4, columnspan=2, sticky=tk.W)
        text_total_page.config(textvariable=self.str_pages)
        self.str_pages.set(self.book_info.pages)

        # ********** 5行目 ********
        # URLラベル
        label_url = ttk.Label(self.sub_window, text="URL:")
        label_url.grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        # URL入力欄
        self.str_url = tk.StringVar()
        text_url = ttk.Entry(self.sub_window, width=100)
        text_url.grid(row=4, column=1, columnspan=5, sticky=tk.W)
        text_url.config(textvariable=self.str_url)
        self.str_url.set(self.book_info.url)

        # ********** 6行目 *********
        # コメントラベル
        label_comment = ttk.Label(self.sub_window, text="コメント：")
        label_comment.grid(row=5, column=0, padx=5, pady=5, sticky=tk.E)
        # フレーム
        frame = ttk.Frame(self.sub_window)
        frame.grid(row=5, column=1, columnspan=5, padx=5, pady=5, sticky=tk.W)
        # コメント入力欄
        self.text_comment = tk.Text(frame, width=100, height=5)
        self.text_comment.pack(side=tk.LEFT)
        self.text_comment.insert(tk.END, self.book_info.comment)
        # 縦スクロールバー
        vscrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        vscrollbar.pack(side=tk.LEFT, fill=tk.Y)
        vscrollbar.config(command=self.text_comment.yview)
        self.text_comment.config(yscrollcommand=vscrollbar.set)
        
        # ********* 7行目 **********
        if self.mode == "add":
            btn_add = ttk.Button(self.sub_window, text="追加")
            btn_add.grid(row=6, column=1, padx=5, pady=5, sticky=tk.E)
            btn_add.config(command=self.add)
        else:
            btn_update = ttk.Button(self.sub_window, text="更新")
            btn_update.grid(row=6, column=4, padx=5, pady=5, sticky=tk.E)
            btn_update.config(command=self.update)

    # サブウィンドウでの入力値の受け取り        
    def get_input_data(self):
        self.book_info.name = self.str_book_title.get()
        self.book_info.auther = self.str_auther.get()
        self.book_info.evaluation = self.str_evaluation.get()
        self.book_info.status = self.str_status.get()
        self.book_info.purchase_date = self.str_purchase_date.get()
        self.book_info.start_date = self.str_start_date.get()
        self.book_info.end_date = self.str_end_date.get()
        self.book_info.pages = self.str_pages.get()
        self.book_info.url = self.str_url.get()
        self.book_info.comment = self.text_comment.get("1.0", "end")
    
    def add(self):
        # 入力値の取り出し
        self.get_input_data()
        
        # 簡単な入力チェック
        if len(self.book_info.name.strip()) == 0:
            messagebox.showerror("エラー", "書籍名が空白です")
            return
        elif self.book_info.pages.isdigit() == False:
            messagebox.showerror("エラー", "ページ数が数字ではありません。")
            return
        
        # インサート実行
        self.book_info.insert(self.db)
        
        # リストの再描画
        self.master.display_list()

        # サブウィンドウを閉じる
        self.sub_window.destroy()
    
    def update(self):
        # 入力値の取り出し
        self.get_input_data()
        # 簡単な入力チェック
        if len(self.book_info.name.strip()) == 0:
            messagebox.showerror("エラー", "書籍名が空白です。")
            return
        elif self.book_info.pages.isdigit() == False:
            messagebox.showerror("エラー", "ページ数が数字ではありません。")
            return
        # update実行
        self.book_info.update(self.db)

        # リストの再描画
        self.master.display_list()

        # サブウィンドウを閉じる
        self.sub_window.destroy()

"""
Bookテーブルクラス
"""
class Book:
    def __init__(self):
        self.id = -1
        self.name = ""
        self.auther = ""
        self.evaluation = EVALUATION_VALUE[0]
        self.status = STATUS_VALUE[1]
        self.purchase_date = ""
        self.start_date = ""
        self.end_date = ""
        self.pages = 0
        self.url = ""
        self.comment = ""
    
    def select_all(self, db):
        db.cursor.execute("select * from books order by id desc")
        books = []
        for row in db.cursor:
            book = Book()
            book.id = row[0]
            book.name = row[1]
            book.auther = row[2]
            book.evaluation = row[3]
            book.status = row[4]
            book.purchase_date = row[5]
            book.start_date = row[6]
            book.end_date = row[7]
            book.pages = row[8]
            book.url = row[9]
            book.comment = row[10]

            books.append(book)
        return books
    
    def select(self, db, id):
        db.cursor.execute(f"select * from books where id={id}")
        result = db.cursor.fetchone()
        book = Book()
        book.id = result[0]
        book.name = result[1]
        book.auther = result[2]
        book.evaluation = result[3]
        book.status = result[4]
        book.purchase_date = result[5]
        book.start_date = result[6]
        book.end_date = result[7]
        book.pages = result[8]
        book.url = result[9]
        book.comment = result[10]

        return book
    
    def insert(self, db):
        db.cursor.execute(f"insert into books(name, auther, evaluation, status,\
                            purchase_date, start_date, end_date, pages, url, comment)"
                          f"values ('{self.name}',"
                                  f"'{self.auther}',"
                                  f"'{self.evaluation}',"
                                  f"'{self.status}',"
                                  f"'{self.purchase_date}',"
                                  f"'{self.start_date}',"
                                  f"'{self.end_date}',"
                                  f"'{self.pages}',"
                                  f"'{self.url}',"
                                  f"'{self.comment}')"
        )
        db.conn.commit()
    
    def update(self, db):
        db.cursor.execute(f"update books "
                          f"set name='{self.name}',"
                          f"auther='{self.auther}',"
                          f"evaluation='{self.evaluation}',"
                          f"status='{self.status}',"
                          f"purchase_date='{self.purchase_date}',"
                          f"start_date='{self.start_date}',"
                          f"end_date='{self.end_date}',"
                          f"pages={self.pages},"
                          f"url='{self.url}',"
                          f"comment='{self.comment}' "
                          f"where id={self.id}")
        db.conn.commit()

    def delete(self, db, id):
        db.cursor.execute(f"delete from books where id={id}")
        db.conn.commit()

"""
データベース管理クラス
"""
class DatabaseSession:
    def __init__(self):
        self.conn = sqlite3.connect("./db/Books.db")
        print("connected")
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        self.conn.close()
        print("disconnected")


if __name__ == "__main__":
    root = tk.Tk()
    mainWindow = MainWindow(master=root)
    mainWindow.mainloop()




