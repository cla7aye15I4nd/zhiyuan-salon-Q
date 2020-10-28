import os
import xlrd
import xlwt

def format_info(info):
    info['学号'] = int(info['学号'])
    info['致远沙龙汇总'] = 0
    info['相关院系汇总'] = 0
    info['总次数'] = 0
    info['是否合格'] = '否'
    return info

def load_info(filename, index, years):
    workbook = xlrd.open_workbook(filename)
    booksheet = workbook.sheet_by_index(index)

    students = []
    keys = [key for key in booksheet.row_values(0) if key]
    level_id = -1
    for i, key in enumerate(keys):
        if key == '年级':
            level_id = i
    
    for row_num in range(1, booksheet.nrows):
        info = booksheet.row_values(row_num)
        year = str(int(info[level_id]))        
        if year in years:
            students.append(format_info(dict(zip(keys, info))))

    return students

def load_salon(save_dir):
    zhiyuan = {}
    other = {}

    for filename in os.listdir(save_dir):
        if not filename.startswith('record'):
            continue

        with open(os.path.join(save_dir, filename)) as f:
            text = f.read().splitlines()

        for names, people in zip(text[::2], text[1::2]):
            for sid in people.strip('、').split('、'):                
                if filename.endswith('other.text'):
                    count = 1
                    if '(' in sid:
                        count = int(sid.split('(')[1][:-1])
                        sid = sid.split('(')[0]
                    other[int(sid)] = other.get(int(sid), 0) + count
                else:
                    zhiyuan[int(sid)] = zhiyuan.get(int(sid), 0) + 1
    return zhiyuan, other

def write_to_sheet(zhiyuan, other, worksheet, students):
    for student in students:
        student['致远沙龙汇总'] = zhiyuan.get(student['学号'], 0)
        student['相关院系汇总'] = other.get(student['学号'], 0)
        student['总次数'] = zhiyuan.get(student['学号'], 0) + other.get(student['学号'], 0)
        student['是否合格'] = '是' if student['总次数'] >= 16 else '否'

    keys = ['学号', '姓名', '性别', '班级', '年级', '专业', '致远沙龙汇总', '相关院系汇总', '总次数', '是否合格']
    for col, key in enumerate(keys):
        worksheet.write(0, col, key)

    style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern_fore_colour = 5
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    style.pattern = pattern
    for row, student in enumerate(students):
        for col, key in enumerate(keys):
            content = str(student[key])
            if student['是否合格'] == '否':
                worksheet.write(row + 1, col, content, style)
            else:
                worksheet.write(row + 1, col, content)

    worksheet.col(0).width = 256 * 15
    worksheet.col(3).width = 256 * 12
    worksheet.col(5).width = 256 * 30
    
def export(years):
    zhiyuan, other = load_salon(os.path.join('.', 'saves'))
    workbook = xlwt.Workbook(encoding = 'utf-8')

    write_to_sheet(zhiyuan, other, workbook.add_sheet('理科'), load_info(os.path.join('.', 'data', 'info.xlsx'), 1, years))
    write_to_sheet(zhiyuan, other, workbook.add_sheet('工科'), load_info(os.path.join('.', 'data', 'info.xlsx'), 2, years))

    directory = os.path.join(os.getcwd(), 'data')
    filename  = '致远沙龙统计.xls'
    workbook.save(os.path.join(directory, filename))
    return directory, filename
