import mdl
from sys import exit
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========
  Checks the commands array for any animation commands
  (frames, basename, vary)
  Should set num_frames and basename if the frames
  or basename commands are present
  If vary is found, but frames is not, the entire
  program should exit.
  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    FRAME_CHECK, BASENAME_CHECK, VARY_CHECK = False, False, False
    name = 'default_name'

    for command in commands:
        c = command['op']
        args = command['args']
        if c == 'frames':
            FRAME_CHECK = True
            num_frames = args[0]
        elif c == 'basename':
            BASENAME_CHECK = True
            name = args[0]
        elif c == 'vary':
            VARY_CHECK = True
        else:
            continue

    if VARY_CHECK and not FRAME_CHECK:
        print('Error: vary found without frames')
        exit()
    if FRAME_CHECK and not BASENAME_CHECK:
        print('Error: frame found without basename')
        print('Set basename to default value \"default_name\"')
    if FRAME_CHECK and VARY_CHECK:
        return (name, num_frames)
    else:
        print('Not enough information to be considered an animation')
        return (name, 1)

"""======== second_pass( commands ) ==========
  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).
  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.
  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(int(num_frames)) ]
    for command in commands:
        c = command['op']
        args = command['args']
        if c == 'vary':
            KNOB_NAME = command['knob']
            start_frame, end_frame = args[0], args[1]
            start_val, end_val = args[2], args[3]
            if end_frame < start_frame:
                print('Error: start frame is greater than end frame')
                break
            if end_frame > num_frames:
                print('Error: end frame is greater than total number of frames')
                break
            frame_difference = end_frame - start_frame
            val_difference = end_val - start_val
            rate = val_difference / frame_difference
            for i in range(int(start_frame),int(end_frame+1)):
                frames[i][KNOB_NAME] = start_val + rate * (i - start_frame)
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    if num_frames > 1:
        frames = second_pass(commands, num_frames)


    tmp = new_matrix()
    ident( tmp )

    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 100
    consts = ''
    coords = []
    coords1 = []

    if num_frames == 1:
        for command in commands:
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0] + '.png')
            # end operation loop
    if num_frames > 1:
        for i in range(len(frames)):
            tmp = new_matrix()
            ident( tmp )

            stack = [ [x[:] for x in tmp] ]
            screen = new_screen()
            zbuffer = new_zbuffer()
            tmp = []
            step_3d = 100
            consts = ''
            coords = []
            coords1 = []
            for knob in frames[i]:
                symbols[knob][1] = frames[i][knob]
            for command in commands:
                c = command['op']
                args = command['args']
                knob_value = 1

                if c == 'box':
                    if command['constants']:
                        reflect = command['constants']
                    add_box(tmp,
                            args[0], args[1], args[2],
                            args[3], args[4], args[5])
                    matrix_mult( stack[-1], tmp )
                    draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                    tmp = []
                    reflect = '.white'
                elif c == 'sphere':
                    if command['constants']:
                        reflect = command['constants']
                    add_sphere(tmp,
                               args[0], args[1], args[2], args[3], step_3d)
                    matrix_mult( stack[-1], tmp )
                    draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                    tmp = []
                    reflect = '.white'
                elif c == 'torus':
                    if command['constants']:
                        reflect = command['constants']
                    add_torus(tmp,
                              args[0], args[1], args[2], args[3], args[4], step_3d)
                    matrix_mult( stack[-1], tmp )
                    draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                    tmp = []
                    reflect = '.white'
                elif c == 'line':
                    add_edge(tmp,
                             args[0], args[1], args[2], args[3], args[4], args[5])
                    matrix_mult( stack[-1], tmp )
                    draw_lines(tmp, screen, zbuffer, color)
                    tmp = []
                elif c == 'move':
                    val = 1
                    if 'knob' in command:
                        knob = command['knob']
                        if knob is not None:
                            val = symbols[knob][1]
                    tmp = make_translate(args[0]*val, args[1]*val, args[2]*val)
                    matrix_mult(stack[-1], tmp)
                    stack[-1] = [x[:] for x in tmp]
                    tmp = []
                elif c == 'scale':
                    val = 1
                    if 'knob' in command:
                        knob = command['knob']
                        if knob is not None:
                            val = symbols[knob][1]
                    tmp = make_scale(args[0]*val, args[1]*val, args[2]*val)
                    matrix_mult(stack[-1], tmp)
                    stack[-1] = [x[:] for x in tmp]
                    tmp = []
                elif c == 'rotate':
                    val = 1
                    if 'knob' in command:
                        knob = command['knob']
                        if knob is not None:
                            val = symbols[knob][1]
                    theta = args[1] * (math.pi/180) * val
                    if args[0] == 'x':
                        tmp = make_rotX(theta)
                    elif args[0] == 'y':
                        tmp = make_rotY(theta)
                    else:
                        tmp = make_rotZ(theta)
                    matrix_mult( stack[-1], tmp )
                    stack[-1] = [ x[:] for x in tmp]
                    tmp = []
                elif c == 'push':
                    stack.append([x[:] for x in stack[-1]] )
                elif c == 'pop':
                    stack.pop()
                # end operation loop
            print('Saving frame: ' + str(i))
            img_name = '00' + str(i)
            img_name = name + img_name[-3:]
            save_extension(screen, 'anim/' + img_name)
        print('Making animation...')
        make_animation(name)
