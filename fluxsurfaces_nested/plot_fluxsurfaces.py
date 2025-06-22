# coding=utf-8

"""
Plot three (partial) nested flux surfaces with field lines.

Examples:
    $ python plot_fluxsurfaces.py
"""

__author__      = "Alf Köhn-Seemann"
__email__       = "koehn@igvp.uni-stuttgart.de"
__copyright__   = "University of Stuttgart"
__license__     = "MIT"


# import standard modules
import argparse
import numpy as np
import mayavi.mlab as mlab


def toroidal_helix( R0=3, a=1, phi=np.linspace(0,1.*np.pi,200), q=2. ):
#{{{

    n = 1./q

    x = (R0 - a*np.cos(n*phi))*np.cos(phi)
    y = (R0 - a*np.cos(n*phi))*np.sin(phi)
    z = a*np.sin(n*phi)

    return x, y, z
#}}}


def make_fluxsurface_coordinates( R0=3., a=1.,
                                  N_theta=200, N_phi=200,
                                  phi_start=0, phi_end=np.pi,
                                  theta_start=0, theta_end=2*np.pi,
                                ):
#{{{

    # theta: poloidal angle | phi: toroidal angle
    
    thetaVals   = np.linspace(theta_start, theta_end, N_theta)
    phiVals     = np.linspace(phi_start, phi_end, N_phi)

    fluxsurface_theta, fluxsurface_phi = np.meshgrid( thetaVals, phiVals )

    # torus parametrization
    xVals   = (R0 + a*np.cos(fluxsurface_theta)) * np.cos(fluxsurface_phi)
    yVals   = (R0 + a*np.cos(fluxsurface_theta)) * np.sin(fluxsurface_phi)
    zVals   = a * np.sin(fluxsurface_theta)

    return xVals, yVals, zVals

#}}}


def make_fieldline_coordinates( R0=3., a=1., q=1.2,
                                phi_start=0, phi_end=np.pi,
                                N_phi=200,
                                torTurns=6
                               ):
#{{{

    for ii in range(torTurns):
        phi_flufla_tmp = np.linspace((2*ii+phi_start/np.pi)*np.pi, (2*ii+phi_end/np.pi)*np.pi, N_phi)
        if ii == 0:
            phi_flufla = phi_flufla_tmp
        else:
            phi_flufla = np.vstack( [phi_flufla, phi_flufla_tmp]  )

        x_coords, y_coords, z_coords = toroidal_helix( R0=R0, a=a, 
                                                       phi=phi_flufla_tmp,
                                                       q=q, )
        fieldline_coords_tmp = np.vstack( [x_coords, y_coords, z_coords] )
        fieldline_coords_tmp = fieldline_coords_tmp.reshape( (1, 
                                                              fieldline_coords_tmp.shape[0], 
                                                              fieldline_coords_tmp.shape[1]) )
        if ii == 0:
            fieldline_coords = fieldline_coords_tmp
        else:
            fieldline_coords = np.vstack( [fieldline_coords, fieldline_coords_tmp] )

    return fieldline_coords
#}}}


def calc_torTurns(q):
#{{{

    # get number of toroidal turns to approximately end back at poloidal 
    # starting position to make it look nicer
    torTurns = 0
    while True:
        # calculate n*iota / (2*pi)
        theta = (torTurns/q)/(2*np.pi)
        #print("torTurns = {0}, theta = {1}".format(torTurns, theta))
        if theta < 1:
            torTurns += 1
        else:
            break

    return torTurns
#}}}


def main():
#{{{

    # initialize parser for command line options
    parser  = argparse.ArgumentParser()
    # add optional arguments
    parser.add_argument( "-f", "--fname_plot", type=str, default='', 
                         help="Filename for plot." )
    # read all arguments from command line
    args        = parser.parse_args()
    fname_plot  = args.fname_plot


    # major and minor radius
    R0, a = 3., 1.

    # magnetic fieldline #1
    a_flufla1   = a*.35
    q_flufla1   = 1.2
    phi_start_1 = 0.
    phi_end_1   = np.pi
    N_phi       = 200

    # get number of toroidal turns to approximately end back at poloidal starting position
    torTurns_1 = calc_torTurns(q_flufla1)

    # get x,y,z coordinates of fieldlines
    fieldline1_coords = make_fieldline_coordinates( R0=R0, a=a_flufla1, q=q_flufla1,
                                                    phi_start=phi_start_1, phi_end=phi_end_1,
                                                    N_phi=N_phi,
                                                    torTurns=torTurns_1 )

    # magnet fieldline #2
    a_flufla2   = a*.75
    q_flufla2   = 1.6
    phi_start_2 = 0.
    phi_end_2   = 0.9*np.pi
    torTurns_2  = calc_torTurns(q_flufla2)

    fieldline2_coords = make_fieldline_coordinates( R0=R0, a=a_flufla2, q=q_flufla2,
                                                    phi_start=phi_start_2, phi_end=phi_end_2,
                                                    N_phi=N_phi,
                                                    torTurns=torTurns_2 )

    # magnetic fieldline #3
    a_flufla3   = a
    q_flufla3   = 2.8
    phi_start_3 = 0.
    phi_end_3   = 0.8*np.pi
    torTurns_3  = calc_torTurns(q_flufla3)

    fieldline3_coords = make_fieldline_coordinates( R0=R0, a=a_flufla3, q=q_flufla3,
                                                    phi_start=phi_start_3, phi_end=phi_end_3,
                                                    N_phi=N_phi,
                                                    torTurns=torTurns_3 )


    fluxsurf1_x, fluxsurf1_y, fluxsurf1_z = make_fluxsurface_coordinates( R0=3., a=a_flufla1,
                                                                          N_theta=200, N_phi=N_phi,
                                                                          phi_start=phi_start_1, phi_end=phi_end_1,
                                                                          theta_start=0, theta_end=2*np.pi )

    fluxsurf2_x, fluxsurf2_y, fluxsurf2_z = make_fluxsurface_coordinates( R0=3., a=a_flufla2,
                                                                          N_theta=200, N_phi=N_phi,
                                                                          phi_start=phi_start_2, phi_end=phi_end_2,
                                                                          theta_start=0, theta_end=2*np.pi )

    fluxsurf3_x, fluxsurf3_y, fluxsurf3_z = make_fluxsurface_coordinates( R0=3., a=a_flufla3,
                                                                          N_theta=200, N_phi=N_phi,
                                                                          phi_start=phi_start_3, phi_end=phi_end_3,
                                                                          theta_start=0, theta_end=2*np.pi )

    mlab.figure( bgcolor=(1., 1., 1.), size=(1000,1000))
    mlab.view(azimuth=90, elevation=125)


    for ii in range(torTurns_1):
        mlab.plot3d( fieldline1_coords[ii,0,:], fieldline1_coords[ii,1,:], fieldline1_coords[ii,2,:], color=(0,0,0) )
    mlab.mesh( fluxsurf1_x, fluxsurf1_y, fluxsurf1_z, color=(.0, .5, 1.) )

    for ii in range(torTurns_2):
        mlab.plot3d( fieldline2_coords[ii,0,:], fieldline2_coords[ii,1,:], fieldline2_coords[ii,2,:], color=(0,0,0) )
    mlab.mesh( fluxsurf2_x, fluxsurf2_y, fluxsurf2_z, color=(.0, .7, 1.) )

    for ii in range(torTurns_3):
        mlab.plot3d( fieldline3_coords[ii,0,:], fieldline3_coords[ii,1,:], fieldline3_coords[ii,2,:], color=(0,0,0) )
    mlab.mesh( fluxsurf3_x, fluxsurf3_y, fluxsurf3_z, color=(.0, .85, 1.) )

    if len(fname_plot) > 0:
        mlab.savefig( fname_plot, size=(4000, 4000) )
    else:
        mlab.show()

#}}}


if __name__ == '__main__':
    main()

