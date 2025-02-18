import os
import re
import unicodedata

import fitz
import pandas as pd
from tqdm.notebook import tqdm, trange


def concat_lines(lines):
    text = ''
    for line in lines:
        for span in line['spans']:
            text += span['text']
    return text


def extract_title(doc):
    page = doc[0]
    texts = page.get_text('dict')
    blocks = texts['blocks']
    for block in blocks:
        if 'lines' in block:
            block['text'] = concat_lines(block['lines']).strip()
        else:
            block['text'] = ''
    blocks = filter(lambda v: v['text'] != '', blocks)
    return list(blocks)[-1]['text']


def extract_bbox(
    doc,
    page_number,
    last_problem=None,
    lecture_name='',
    header_threshold=40,
    footer_threshold=750,
    left_indent_threshold=44,
    side_note_threshold=395,
    verbose=False,
):
    problems = []
    page = doc[page_number - 1]
    texts = page.get_text('dict')
    blocks = texts['blocks']
    page_w = texts['width']
    # page_h = texts['height']
    problem_id = 0
    if last_problem is None:
        lecture_id = ''
        chapter_id, chapter_name = 0, ''
        section_id, section_name = 0, ''
        subsection_name = ''
    else:
        lecture_id = last_problem['lecture_id']
        chapter_id, chapter_name = last_problem['chapter_id'], last_problem['chapter_name']
        section_id, section_name = last_problem['section_id'], last_problem['section_name']
        subsection_name = last_problem['subsection_name']
    for block in blocks:
        if 'lines' in block:
            block['text'] = concat_lines(block['lines']).strip()
        else:
            block['text'] = ''
    blocks = filter(lambda v: v['text'] != '', blocks)  # remove empty block
    images = []
    for image in page.get_image_info():
        bbox = image['bbox']
        if bbox[0] >= left_indent_threshold:
            image['text'] = ''
            images.append(image)
    drawings = []
    for info in page.get_drawings():
        bbox = tuple(info['rect'])
        if bbox[0] >= left_indent_threshold:
            drawings.append(dict(bbox=bbox, text=''))
    elements = list(blocks) + list(images) + list(drawings)
    elements = filter(
        lambda v: v['bbox'][0] <= side_note_threshold, elements
    )  # remove side notes (x0)
    elements = filter(lambda v: v['bbox'][1] <= footer_threshold, elements)  # remove footer (y0)
    elements = sorted(elements, key=lambda v: v['bbox'][1])  # sorted (y0)
    for _idx, element in enumerate(elements):
        bbox = element['bbox']
        text = element['text']
        x0, y0, x1, y1 = bbox
        is_new_section, is_main_text = False, True
        if y0 <= header_threshold:
            # extract info from the header
            if match := re.match(r'^([A-Z|a-z|Ａ-Ｚ|ａ-ｚ]+)(\d+|[０-９]+)(.+)【.+】', text):
                # extract chapters (e.g., A01 ...【...】)
                lecture_id = unicodedata.normalize('NFKC', match[1])
                chapter_id = int(match[2])
                chapter_name = match[3]
            is_new_section = False
            is_main_text = False
        elif x0 < left_indent_threshold:
            # extract info from the main text
            if match := re.match(r'^(\d+|[０-９]+)\.(.+)$', text):
                # extract sections (e.g., 1. ...)
                section_id = int(match[1])
                section_name = match[2]
                subsection_name = ''
                problem_id = 0
                is_new_section = True
                is_main_text = False
            elif match := re.match(r'^【(.+)】', text):
                # extract subsections (e.g., 【...】)
                subsection_name = match[1]
                is_new_section = False
                is_main_text = False
            elif match := re.match(r'^□([①-⑳|㉑-㊿])(.+)$', text):
                # extract problems (e.g., □① ...)
                problem_id = int(unicodedata.normalize('NFKC', match[1]))
                is_new_section = True
                is_main_text = True
        if is_new_section:
            problems.append(
                dict(
                    bboxes=[],
                    page_number=page_number,
                    lecture_id=lecture_id,
                    lecture_name=lecture_name,
                    chapter_id=chapter_id,
                    chapter_name=chapter_name,
                    section_id=section_id,
                    section_name=section_name,
                    subsection_name=subsection_name,
                    problem_id=problem_id,
                    text_length=0,
                )
            )
        if is_main_text and len(problems) > 0:
            problems[-1]['bboxes'].append(bbox)
            problems[-1]['text_length'] += len(text)
        if verbose:
            bbox_str = ','.join(map('{:3.0f}'.format, bbox))
            print(
                '{} p.{:<3} {:>2} {:>2} ({:>3},{:>3},{:>3}): {}'.format(
                    bbox_str,
                    page_number,
                    is_main_text,
                    lecture_id,
                    chapter_id,
                    section_id,
                    problem_id,
                    text,
                )
            )
    problems = filter(lambda v: len(v['bboxes']) > 0, problems)
    problems = filter(lambda v: v['text_length'] > 0, problems)
    problems = list(problems)
    y0_acc = [problem['bboxes'][0][1] for problem in problems]
    y0_acc.append(footer_threshold)
    for problem_id, (y0, y1) in enumerate(zip(y0_acc[:-1], y0_acc[1:], strict=False)):
        tables = page.find_tables(clip=(0, y0, int(page_w), y1))
        for _idx, table in enumerate(tables.tables):
            if table.bbox[0] <= side_note_threshold and table.bbox[1] <= footer_threshold:
                problems[problem_id]['bboxes'].append(table.bbox)
    for problem in problems:
        bboxes = problem['bboxes']
        x0 = min(map(lambda t: t[0], bboxes))
        y0 = min(map(lambda t: t[1], bboxes))
        x1 = max(map(lambda t: t[2], bboxes))
        y1 = max(map(lambda t: t[3], bboxes))
        problem['bbox'] = (x0, y0, x1, y1)
        problem['within_main_view'] = (
            (y0 >= header_threshold) and (y1 <= footer_threshold) and (x1 <= side_note_threshold)
        )
    return problems


def render_problems(problems, doc_dict, save_dir, dpi=200, add_prefix=True, dry_run=False):
    pbar = tqdm(problems)
    for idx, problem in enumerate(pbar):
        pbar.set_description('画像出力中')
        lecture_id = problem['lecture_id']
        chapter_id = problem['chapter_id']
        section_id = problem['section_id']
        problem_id = problem['problem_id']
        for doc_type_name, doc in doc_dict.items():
            page = doc[problem['page_number'] - 1]
            tar_pix = page.get_pixmap(clip=problem['bbox'], dpi=dpi)
            if not problem['within_main_view']:
                tar_pix.clear_with(255)
                for bbox in problem['bboxes']:
                    src_pix = page.get_pixmap(clip=bbox, dpi=dpi)
                    tar_pix.copy(src_pix, src_pix.irect)
            file_name = '{:02d}_{:02d}_{:02d}_{}'.format(
                chapter_id, section_id, problem_id, doc_type_name
            )
            if add_prefix:
                file_name = '{:04d}_{}'.format(idx + 1, file_name)
            file_name = f'{lecture_id}_{file_name}'
            problem[f'{doc_type_name}_file'] = file_name
            if dry_run:
                print(file_name)
            else:
                path = f'{save_dir}/{file_name}.png'
                os.makedirs(os.path.dirname(path), exist_ok=True)
                tar_pix.save(path)


def create_accumulated_csv(problems, delimiter=' '):
    rows = []
    for problem in problems:
        blank_name = '<img src="{}.png" />'.format(problem['blank_file'])
        filled_name = '<img src="{}.png" />'.format(problem['filled_file'])
        page_number = problem['page_number']
        lecture_id, lecture_name = problem['lecture_id'], problem['lecture_name']
        chapter_id, chapter_name = '{:02d}'.format(problem['chapter_id']), problem['chapter_name']
        section_id, section_name = '{:d}'.format(problem['section_id']), problem['section_name']
        subsection_name = problem['subsection_name']
        rows.append(
            [
                blank_name,
                filled_name,
                lecture_name,
                page_number,
                lecture_id,
                chapter_id,
                chapter_name,
                section_id,
                section_name,
                subsection_name,
            ]
        )
    df = pd.DataFrame(
        rows,
        columns=[
            'blank',
            'filled',
            'lecture_name',
            'page_number',
            'lecture_id',
            'chapter_id',
            'chapter_name',
            'section_id',
            'section_name',
            'subsection_name',
        ],
    )
    return df


def run_all(
    blank_file,
    filled_file,
    output_folder,
    dpi=200,
    kw_extract_box=None,
    kw_render_problems=None,
):
    kw_extract_box = (
        dict(
            header_threshold=40,
            footer_threshold=750,
            left_indent_threshold=44,
            side_note_threshold=395,
            verbose=False,
        )
        if kw_extract_box is None
        else kw_extract_box
    )
    kw_render_problems = (
        dict(add_prefix=True, dry_run=False) if kw_render_problems is None else kw_render_problems
    )
    doc_blk = fitz.open(blank_file)
    doc_fld = fitz.open(filled_file)
    print(f'Info: ファイルの読み込み成功（{blank_file} & {filled_file}）')
    assert len(doc_blk) == len(doc_fld), 'Error: ページ数が一致しません！ファイルを確認してください'

    problems = []
    last_problem = None
    lecture_name = extract_title(doc_blk)
    pbar = trange(1, len(doc_fld) + 1)
    for page_number in pbar:
        pbar.set_description('問題抽出中')
        out = extract_bbox(
            doc_fld,
            page_number,
            last_problem=last_problem,
            lecture_name=lecture_name,
            **kw_extract_box,
        )
        problems += out
        if len(problems) > 0:
            last_problem = problems[-1]

    render_problems(
        problems,
        dict(filled=doc_fld, blank=doc_blk),
        f'{output_folder}/png',
        dpi=dpi,
        **kw_render_problems,
    )

    df = create_accumulated_csv(problems)
    path = f'{output_folder}/info.csv'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, header=False, index=False)
