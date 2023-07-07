# - *- coding: utf-8 -*-

import os
import json
from pathlib import Path
from typing import List
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from typing import Tuple
import re

class CMainWindow():
    def __init__(self) -> None:
        self._main_form = tk.Tk()
        self._main_form.title('Markdown标题添加编号 v1.1')
        self._main_form.geometry('800x140+500+300')
        self._main_form.resizable(0, 0) # 禁止拉伸窗口
        #self._main_form.attributes("-toolwindow", 2) # 去掉窗口最大化最小化按钮，只保留关闭
        '''
        Markdown标题添加编号 v1.1                                                                  - + X  |
        =================================================================================================
        |   输入文件  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx     |
        -------------------------------------------------------------------------------------------------
        |   输出文件  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx     |
        -------------------------------------------------------------------------------------------------
        |   起始等级   #     ▽     图片地址替换为相对地址   |选择文件|  |清除历史|  |删除编号|  |添加编号|    |
        =================================================================================================
        '''
        self._label1 = tk.Label(master=self._main_form, text='输入文件')
        self._label1.pack()
        self._label1.place(x=18, y=22)

        # self.__input_file = tk.Entry(master=self._main_form, width=72)
        # self.__input_file.pack()
        # self.__input_file.place(x=75, y=25)

        self._input_file = tk.ttk.Combobox(master=self._main_form, width=99)
        self._input_file.bind('<<ComboboxSelected>>', self._selected_history_item)
        self._input_file.pack()
        self._input_file.place(x=75, y=25)

        self._label2 = tk.Label(master=self._main_form, text='输出文件')
        self._label2.pack()
        self._label2.place(x=18, y=62)

        self._output_file = tk.Entry(master=self._main_form, width=101)
        self._output_file.pack()
        self._output_file.place(x=75, y=65)

        self._label3 = tk.Label(master=self._main_form, text='起始等级')
        self._label3.pack()
        self._label3.place(x=18, y=102)

        self._start_level = ttk.Combobox(master=self._main_form, width=25, state='readonly')
        self._start_level.pack()
        self._start_level.place(x=75, y=102)
        self._start_level['values'] = ('#', '##', '###', '####', '#####')
        self._start_level.current(0)

        self._solve_image_path = tk.Button(master=self._main_form, text='图片地址替换为相对地址', command=self._solve_image_path, width=20, height=1)
        self._solve_image_path.pack()
        self._solve_image_path.place(x=320, y=100)

        self._button_select = tk.Button(master=self._main_form, text='选择文件', command=self._select_md_file, width=8, height=1)
        self._button_select.pack()
        self._button_select.place(x=510, y=100)

        self._button_clear_history = tk.Button(master=self._main_form, text='清除历史', command=self._clear_history, width=8, height=1)
        self._button_clear_history.pack()
        self._button_clear_history.place(x=580, y=100)

        self._button_delete_number = tk.Button(master=self._main_form, text='删除编号', command=self._delete_number, width=8, height=1)
        self._button_delete_number.pack()
        self._button_delete_number.place(x=650, y=100)

        self._button_number_title = tk.Button(master=self._main_form, text='添加编号', command=self._add_number, width=8, height=1)
        self._button_number_title.pack()
        self._button_number_title.place(x=720, y=100)
        # 加载历史记录
        self._history = {}
        self._history_file: Path = Path(__file__).parent / 'history.json'
        self._load_history()
    
    def _load_history(self) -> None:
        if not self._history_file.is_file():
            return
        history_json_str = self._history_file.read_text(encoding='utf-8')
        self._history = json.loads(history_json_str)
        self._input_file['value'] = list(self._history.keys())[::-1] if self._history else []

    def _save_history(self) -> None:
        history_json_str = json.dumps(self._history, ensure_ascii=False, indent=4)
        self._history_file.write_text(history_json_str, encoding='utf-8')

    def _selected_history_item(self, event) -> None:
        input_file_name = self._input_file.get()
        selected_item = self._history.get(input_file_name, {})
        output_file_name = selected_item.get('output', '')
        start_level = selected_item.get('level', 0)
        self._input_file.icursor(0)
        self._output_file.delete(0, tk.END)
        self._output_file.insert(0, output_file_name)
        self._output_file.icursor(0)
        self._start_level.current(start_level - 1)

    def _solve_image_path(self) -> None:
        '''图片地址替换为相对地址'''
        input_file_name = self._input_file.get()
        if not input_file_name:
            messagebox.showerror('没有指定输入文件', '请先选择输入文件！')
            return
        if not os.path.isfile(input_file_name):
            messagebox.showerror('输入文件不存在', '请选择正确的输入文件！')
            return
        output_file_name = self._output_file.get()
        if not output_file_name:
            messagebox.showerror('没有指定输出文件', '请先填写输出文件！')
            return
        with open(input_file_name, 'r', encoding='utf-8') as md_file:
            contents = md_file.readlines()
            contents = CMainWindow.solve_image_path(input_file_name, output_file_name, contents)
            CMainWindow.save_lines_to_file(contents, output_file_name)
        messagebox.showinfo('图片地址替换为相对地址', '完成！')

    def _select_md_file(self) -> None:
        selected_file = filedialog.askopenfilename(title='选择Markdown文件', filetypes=[('Markdown', '*.md'), ('All Files', '*.*')])
        self._input_file.delete(0, tk.END)
        self._input_file.insert(0, selected_file)
        self._input_file.icursor(0)
        self._output_file.delete(0, tk.END)
        self._output_file.insert(0, selected_file)
        self._output_file.icursor(0)

    def _clear_history(self) -> None:
        self._history.clear()
        self._save_history()
        self._load_history()
        
    def _check_input_output_path(self) -> Tuple[bool, str, str]:
        input_file_name = self._input_file.get()
        if not input_file_name:
            messagebox.showerror('没有指定输入文件', '请先选择输入文件！')
            return False, '', ''
        if not os.path.isfile(input_file_name):
            messagebox.showerror('输入文件不存在', '请选择正确的输入文件！')
            return False, '', ''
        output_file_name = self._output_file.get()
        if not output_file_name:
            messagebox.showerror('没有指定输出文件', '请先填写输出文件！')
            return False, '', ''
        return True, input_file_name, output_file_name

    def _delete_number(self) -> None:
        ret, input_file_name, output_file_name = self._check_input_output_path()
        if not ret:
            return
        with open(input_file_name, 'r', encoding='utf-8') as md_file:
            contents = md_file.readlines()
            contents = CMainWindow.remove_md_title_number(contents)
            CMainWindow.save_lines_to_file(contents, output_file_name)
        messagebox.showinfo('删除编号', '完成！')
    
    def _add_number(self) -> None:
        input_file_name = self._input_file.get()
        if not input_file_name:
            messagebox.showerror('没有指定输入文件', '请先选择输入文件！')
            return
        if not os.path.isfile(input_file_name):
            messagebox.showerror('输入文件不存在', '请选择正确的输入文件！')
            return
        output_file_name = self._output_file.get()
        if not output_file_name:
            messagebox.showerror('没有指定输出文件', '请先填写输出文件！')
            return
        with open(input_file_name, 'r', encoding='utf-8') as md_file:
            contents = md_file.readlines()
            contents = CMainWindow.remove_md_title_number(contents)
            start_level = self._start_level.get().count('#')
            contents = CMainWindow.generate_md_title_number(contents, start_level)
            CMainWindow.save_lines_to_file(contents, output_file_name)
        if input_file_name in self._history:
            self._history.pop(input_file_name)
        while len(self._history) >= 20: # 只保留20个
            self._history.pop(list(self._history.keys())[0])
        self._history[input_file_name] = {
            'output': output_file_name,
            'level': start_level
        }
        self._save_history()
        self._load_history()
        messagebox.showinfo('添加编号', '完成！')

    @staticmethod
    def solve_image_path(input_md_path, output_md_path: str, md_content: List[str]) -> List[str]:
        input_path = Path(input_md_path)
        output_path = Path(output_md_path)
        for line_number, cur_line in enumerate(md_content):
            # 处理![]()格式的图片
            match_result = re.findall(r'(?:!\[.*\]\((.*?)\))', cur_line)
            if match_result:
                for image in match_result:
                    relpath = CMainWindow._get_relative_path(image, input_path, output_path)
                    cur_line = cur_line.replace(image, relpath)
                # 此行有图片地址，不管有没有真正替换路径，都重新赋值一下没关系
                md_content[line_number] = cur_line
            # 处理<img src=''/>、<img src=''></img>、<img src=""/>、<img src=""></img>等格式的图片
            # 这里两个if不能if-else处理，可能存在一行中同时有两种格式的图片
            if '<img' in cur_line:
                # 提取所有的src=
                match_result = re.findall(r'''(?:<img[^>]*src=["'](.*?)["'])''', cur_line)
                if match_result:
                    for image in match_result:
                        relpath = CMainWindow._get_relative_path(image, input_path, output_path)
                        cur_line = cur_line.replace(image, relpath)
                    # 此行有图片地址，不管有没有真正替换路径，都重新赋值一下没关系
                    md_content[line_number] = cur_line
        return md_content
    
    @staticmethod
    def _get_relative_path(cur_path: str, input_path: Path, output_path: Path) -> str:
        if cur_path.startswith(('http://', 'https://')):
            return cur_path
        image_path = Path(cur_path)
        image_path = (input_path.parent / image_path, image_path)[image_path.is_absolute()]
        if image_path.exists() and image_path.anchor == output_path.anchor:
            # 文件存在再处理
            # image_path = image_path.relative_to(output_path.parent)
            relpath = os.path.relpath(image_path, output_path.parent)
            return relpath
        return cur_path

    @staticmethod
    def remove_md_title_number(md_content: List[str]) -> List[str]:
        level = 0
        for line_number, cur_line in enumerate(md_content):
            if cur_line.startswith('# '):
                level = 1
            elif cur_line.startswith('## '):
                level = 2
            elif cur_line.startswith('### '):
                level = 3
            elif cur_line.startswith('#### '):
                level = 4
            elif cur_line.startswith('##### '):
                level = 5
            elif cur_line.startswith('###### '):
                level = 6
            else:
                continue
            for title_word in range(level + 1, len(cur_line)):
                if not cur_line[title_word].isdigit() and not cur_line[title_word] == '.':
                    md_content[line_number] = f"{cur_line[0:level + 1]}{cur_line[title_word:].lstrip(' ')}"
                    break
        return md_content

    @staticmethod
    def generate_md_title_number(md_content: List[str], start_level: int) -> List[str]:
        cur_level_number = [0, 0, 0, 0, 0, 0]
        level = 0
        for line_number, cur_line in enumerate(md_content):
            if cur_line.startswith('# ') and start_level <= 1:
                level = 1
            elif cur_line.startswith('## ') and start_level <= 2:
                level = 2
            elif cur_line.startswith('### ') and start_level <= 3:
                level = 3
            elif cur_line.startswith('#### ') and start_level <= 4:
                level = 4
            elif cur_line.startswith('##### ') and start_level <= 5:
                level = 5
            elif cur_line.startswith('###### ') and start_level <= 6:
                level = 6
            else:
                continue
            title = cur_line[level + 1:]
            # 跳过附录A和附录B
            if title.startswith(('A.', 'B.')):
                break
            cur_level = level - start_level
            cur_level_number[cur_level] += 1
            for i in range(cur_level + 1, len(cur_level_number)):
                cur_level_number[i] = 0
            title_number = ''
            for i in range(0, cur_level + 1):
                title_number = f'{title_number}{cur_level_number[i]}.'
            title_number = title_number.rstrip('.')
            md_content[line_number] = f'{cur_line[0 : level + 1]}{title_number} {cur_line[level + 1:]}'
        return md_content

    @staticmethod
    def save_lines_to_file(md_content: List[str], file_name: str) -> None:
        with open(file_name, 'w', encoding='utf-8') as md_file:
            md_file.writelines(md_content)
        
    def start(self) -> None:
        self._main_form.mainloop()

if __name__ == '__main__':
    main_window = CMainWindow()
    main_window.start()
