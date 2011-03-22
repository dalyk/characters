#!/usr/bin/python
# recordrecognitionrtsubmission.py -- Stores the data from the recognition rt submission
from __future__ import with_statement
import os, re
import sys
import shutil
from alphabetspaths import *
from matlabutil import format_for_matlab
from image_anonymizer import deanonymize_image
import turkutil


#def get_submission_paths(submission_dict, if_rejected=TURK_RECOGNITION_REJECTED_PATH, if_accepted=TURK_RECOGNITION_PATH, if_none=TURK_RECOGNITION_UNREVIEWED_PATH):
#    return turkutil.get_submission_paths(submission_dict, if_rejected, if_accepted, if_none)


def _make_folder_for_submission(uid, path=RECOGNITION_RT_UNREVIEWED_PATH, return_num=True):
    return turkutil.make_folder_for_submission(uid, path, return_num=return_num)


_BOOL_DICT = {'true':True, 'false':False, 'True':True, 'False':False, '0':False, '1':True, 0:False, 1:True, 'Did Not See':None, 'did not see':None}

def _make_summary(properties):
    rtn = []
    rtn.append('Summary:')
    calibration_task_regex = re.compile('^calibration_task-([0-9]+)-time-of-showCharacters$')
    task_regex = re.compile('^task-([0-9]+)-time-of-showCharacters$')
    calibration_start_time = 'calibration_task-%d-time-of-showCharacters'
    calibration_end_time = 'calibration_task-%d-time-of-keypress'
    task_start_time = 'task-%d-time-of-showCharacters'
    task_end_time = 'task-%d-time-of-keypress'
    task_desc = '%%(task-%(task)d-character-0-alphabet)s, %%(task-%(task)d-character-0-character-number)s, %%(task-%(task)d-character-0-id)s VS. ' + \
            '%%(task-%(task)d-character-1-alphabet)s, %%(task-%(task)d-character-1-character-number)s, %%(task-%(task)d-character-1-id)s'

    calibration_numbers = list(sorted(int(calibration_task_regex.match(key).groups()[0]) for key in properties
        if 'calibration' in key and '-time-of-showCharacters' in key))
    task_numbers = list(sorted(int(task_regex.match(key).groups()[0]) for key in properties
        if 'calibration' not in key and '-time-of-showCharacters' in key))
    
    rtn.append('\nCalibration:')
    total_time, task_count = 0, 0
    for i in calibration_numbers:
        task_count += 1
        cur_time = int(properties[calibration_end_time % i]) - int(properties[calibration_start_time % i])
        total_time += cur_time
        rtn.append('\n%d' % cur_time)
    rtn.append('\nAverage: %d\n\n' % int(total_time / task_count))
    
    rtn.append('\nTasks:')
    for i in task_numbers:
        rtn.append('\nTask %d: %s' % (i, ((task_desc % {'task':i}) % properties)))
        is_correct = _BOOL_DICT[properties['task-%d-is-correct-answer' % i]]
        are_same = _BOOL_DICT[properties['task-%d-are-same' % i]]
        rtn.append('\nTask %d: ' % i)
        if is_correct: rtn.append('Right, ')
        else: rtn.append('Wrong, ')
        if are_same: rtn.append('Are Same')
        else: rtn.append('Are Different')
        if (task_end_time % i) in properties:
            start_time = int(properties[task_start_time % i])
            end_time = int(properties[task_end_time % i])
            rtn.append('\nTask %d RT: %d' % (i, end_time - start_time))
    return ''.join(rtn)

    

def _make_matlab(properties, uid,
                 not_use=('^ipAddress',
                          '^annotation', '^assignmentaccepttime', '^assignmentapprovaltime',
                          '^assignmentduration', '^assignmentrejecttime', '^assignments',
                          '^assignmentstatus', '^assignmentsubmittime', '^autoapprovaldelay',
                          '^autoapprovaltime', '^creationtime', '^deadline', '^description',
                          '^hitlifetime', '^hitstatus', '^hittypeid', '^keywords',
                          '^numavailable', '^numcomplete', '^numpending', '^reviewstatus',
                          '^reward', '^title', '^hitid', '^assignmentid'),
                 quiet=True, zero_based_num=0):
    rtn = []
    uid = uid.replace('-', 'm')
    def can_use(key):
        for bad_key in not_use:
            if re.match(bad_key, key):
                return False
        return True
    for key in sorted(properties.keys()):
        if can_use(key):
            use_key = key.replace('-', '_')
            if 'task_' in use_key:
                tag = use_key[:len('task_')+use_key.index('task_')-1]
                rest = use_key[len(tag)+1:].split('_')
                use_key = '%s(%d).%s' % (tag, int(rest[0]) + 1, '_'.join(rest[1:]))
            rtn.append('results.for_%s(%d).%s = %s;' % (uid, zero_based_num+1, use_key, 
                format_for_matlab(turkutil.string_to_object(properties[key]))))
    return '\n'.join(rtn)
    

def _put_summary(folder, properties, file_name, quiet=True):
    turkutil.put_summary(folder, properties, file_name, _make_summary, quiet=quiet)
    
def _put_matlab(folder, properties, file_name, uid, quiet=True, **kwargs):
    push_dir(folder)
    matlab = _make_matlab(properties, uid, quiet=quiet, **kwargs)
    if not quiet and os.path.exists(file_name):
        input("The file `%s' in `%s' already exists.  Press enter to continue, or ^c (ctrl + c) to break." % (file_name, folder))
    with open(file_name, 'w') as f:
        f.write(matlab)
    pop_dir()
    

def _make_file_name(uid, summary=False, matlab=False):
    if summary:
        return uid.replace('-', 'm') + '_summary.txt'
    elif matlab:
        return uid.replace('-', 'm') + '_matlab.m'
    else:
        return uid.replace('-', 'm') + '_results.txt'


def _record_reaction_times(properties, overwrite=True, tags=('task-', 'calibration_task-'),
        start_time_end='-time-of-showCharacters', end_time_end='-time-of-keypress', find_nums='-time-of-showCharacters',
        if_none=-1):
    if not overwrite: properties = dict(properties)
    for tag in tags:
        cur_regex = re.compile('^%s([0-9]+)' % tag)
        pre_nums = (cur_regex.match(key) for key in properties if tag in key and find_nums in key)
        nums = list(sorted(set(int(match.groups()[0]) for match in pre_nums if match)))
        start_time_key = '%s%%d%s' % (tag, start_time_end)
        end_time_key = '%s%%d%s' % (tag, end_time_end)
        for i in nums:
            if (start_time_key % i) in properties and (end_time_key % i) in properties:
                properties['%s%d-reaction-time' % (tag, i)] = str(int(properties[end_time_key % i]) - int(properties[start_time_key % i]))
            else:
                properties['%s%d-reaction-time' % (tag, i)] = str(if_none)
    return properties


def record_submission(form_dict, many_dirs=True, path=RECOGNITION_RT_UNREVIEWED_PATH,
                      verbose=True, pseudo=False, quiet=True, exclude_rejected=False):
    accepted, rejected = turkutil.get_accepted_rejected_status(form_dict)
    if rejected and exclude_rejected:
        print('Submission rejected.')
        return False
    if verbose: print('Hashing IP address...')
    uid = turkutil.make_uid(form_dict)
    results_num = 0
    if many_dirs:
        if verbose: print('Done.  It\'s %s.<br>Making folder for your submission...' % uid)
        path, results_num = _make_folder_for_submission(uid, path=path, return_num=True)
    if verbose: print('Done<br>Storing your responses...')
    form_dict = turkutil.deanonymize_urls(form_dict)
    form_dict = _record_reaction_times(form_dict)
    try:
        turkutil.put_properties(path, form_dict, _make_file_name(uid), quiet=quiet)
        if not pseudo:
            if verbose: print('Done<br>Summarizing your responses...')
            _put_summary(path, form_dict, _make_file_name(uid, summary=True), quiet=quiet)
            if verbose: print('Done<br>Making a matlab file for your responses...')
            _put_matlab(path, form_dict, _make_file_name(uid, matlab=True), uid, quiet=quiet, zero_based_num=results_num)
        if many_dirs:
            turkutil.log_success(path)
    except KeyError as ex:
        print('<br />  <strong>Error</strong>: %s. Failed to save.  Moving data to bad subdirectory.' % ex)
        new_path = os.path.join(path, '../../BAD')
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        shutil.move(path, new_path)
    if verbose: print('Done<br>You may now leave this page.<br>')
    if verbose: print('<a href="http://scripts.mit.edu/~jgross/alphabets/">Return to home page</a>')
