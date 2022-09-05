import json
import os
import subprocess
import sys

mkvToolsFolder = "C:/Program Files/MKVToolNix/"
editToolName = "mkvpropedit"
infoToolName = "mkvinfo"
mergeToolName = "mkvmerge"
exeExt = ".exe"


if (len(sys.argv) < 2):
    raise Exception('No path specified')

targetDirPath = sys.argv[1]

editToolPath = mkvToolsFolder + editToolName + exeExt
infoToolPath = mkvToolsFolder + infoToolName + exeExt
mergeToolPath = mkvToolsFolder + mergeToolName + exeExt



class ATrack(object):
    track_id : int
    track_name : str
    language : str
    default_track : bool
    forced_track : bool
    type : str



def get_tracks (origItemPath) -> list[ATrack] :
    tracks = list[ATrack]()
    info_json = json.loads(subprocess.check_output([mergeToolPath, '-J', origItemPath]).decode())
                
    for track in info_json['tracks']:
        new_track = ATrack()
        properties = track['properties']
        if 'track_name' in properties:
            new_track.track_name = properties['track_name']
        if 'language' in properties:
            new_track.language = properties['language']
        if 'default_track' in properties:
            new_track.default_track = properties['default_track']
        if 'forced_track' in properties:
            new_track.forced_track = properties['forced_track']
        new_track.type = track['type']
        tracks.append(new_track)
    
    return tracks



def update_file_info(filePath:str, eng_id:int, wrong_ids: list[int]):
    if eng_id < 1:
        return

    args = list[str]()
    args.append(editToolName)
    args.append(filePath)
    # args.append('"{}"'.format(filePath))
    args.extend(['--edit', f'track:a{eng_id}', '--set', 'flag-default=1'])

    for wrong_id in wrong_ids:
        args.extend(['--edit', f'track:a{wrong_id}', '--set', 'flag-default=0'])
    
    argLine = subprocess.list2cmdline(args)
    print(argLine)
    try:
        subprocess.run(args, check=True)
        print('success')
    except:
        print('fail', sys.exc_info()[0])




def update_files(dirPath):
    for itemName in os.listdir(dirPath):
        origItemPath = os.path.join(targetDirPath, itemName)
        if os.path.isfile(origItemPath):
            tracks = get_tracks(origItemPath)
            eng_id = -1
            wrong_ids = list[int]()
            i = 1
            for track in tracks:
                if (track.type != 'audio'): continue                

                if (track.language == 'eng' and track.default_track != True):
                    eng_id = i
                elif (track.language != 'eng' and track.default_track == True):
                    wrong_ids.append(i)

                i += 1
            
            update_file_info(origItemPath, eng_id, wrong_ids)



update_files(targetDirPath)