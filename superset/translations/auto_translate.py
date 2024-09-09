# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import os
import sys

import polib


def split_untranslated_entries():
    # 加载 .po 文件
    current_dir = os.path.dirname(__file__)
    po = polib.pofile(os.path.join(current_dir, 'zh/LC_MESSAGES/messages.po'))
    # 遍历条目
    slice_index = 0
    slice_po = None
    slice_size = 0
    slice_limit = 1024
    total_untranslated = 0
    for entry in po:
        # 打印未翻译的条目
        if (not entry.msgstr and len(entry.msgstr_plural) == 0) or entry.fuzzy:
            print(f'Source: {entry.msgid}')
            print(f'Translation: {entry.msgstr}')
            if slice_po is None or (
                slice_size > 0 and slice_size + len(entry.msgid) > slice_limit):
                if slice_po is not None:
                    slice_po.save(os.path.join(current_dir,
                                               f'zh/LC_MESSAGES/messages_{slice_index + 1}.po'))
                    slice_po = None
                    slice_index += 1
                slice_size = 0
                slice_po = polib.POFile()
                slice_po.metadata = po.metadata
            slice_size += len(entry.msgid)
            if entry.fuzzy:
                entry.flags.remove('fuzzy')
            entry.msgstr = ''
            slice_po.append(entry)
            total_untranslated += 1
    if slice_po is not None:
        slice_po.save(os.path.join(current_dir,
                                   f'zh/LC_MESSAGES/messages_{slice_index + 1}.po'))
    print(f'total untranslated: {total_untranslated}')


def merge_translated_entries():
    current_dir = os.path.dirname(__file__)
    # 遍历current_dir/zh/LC_MESSAGES/messages_*_translated.po文件
    translated_entries = {}
    for filename in os.listdir(os.path.join(current_dir, 'zh/LC_MESSAGES')):
        if filename.endswith('_translated.po'):
            translated_po = polib.pofile(
                os.path.join(current_dir, 'zh/LC_MESSAGES', filename))
            for entry in translated_po:
                if not entry.fuzzy and (
                    entry.msgstr != '' or len(entry.msgstr_plural) > 0):
                    translated_entries[entry.msgid] = (
                    entry.msgstr, entry.msgstr_plural)
    po = polib.pofile(os.path.join(current_dir, 'zh/LC_MESSAGES/messages.po'))
    for entry in po:
        if entry.msgid in translated_entries:
            entry.msgstr = translated_entries[entry.msgid][0]
            entry.msgstr_plural = translated_entries[entry.msgid][1]
            if entry.fuzzy:
                entry.flags.remove('fuzzy')
    po.save(os.path.join(current_dir, 'zh/LC_MESSAGES/messages.po'))


if __name__ == '__main__':
    if sys.argv[1] == 'split':
        split_untranslated_entries()
    elif sys.argv[1] == 'merge':
        merge_translated_entries()
    else:
        print('Usage: python auto_translate.py split|merge')
