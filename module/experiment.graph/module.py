#
# Collective Knowledge (various graphs for experiment)
#
# See CK LICENSE.txt for licensing details
# See CK Copyright.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://cTuning.org/lab/people/gfursin
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# plot universal graph by flat dimensions

def plot(i):
    """

    Input:  {
              Select entries or table:
                 (repo_uoa) or (experiment_repo_uoa)     - can be wild cards
                 (remote_repo_uoa)                       - if remote access, use this as a remote repo UOA
                 (module_uoa) or (experiment_module_uoa) - can be wild cards
                 (data_uoa) or (experiment_data_uoa)     - can be wild cards

                 (repo_uoa_list)                       - list of repos to search
                 (module_uoa_list)                     - list of module to search
                 (data_uoa_list)                       - list of data to search

                 (search_dict)                         - search dict
                 (ignore_case)                         - if 'yes', ignore case when searching

                       OR 

                 table                                 - experiment table (if drawing from other functions)


              (flat_keys_list)                      - list of flat keys to extract from points into table
                                                      (order is important: for example, for plot -> X,Y,Z)

              (flat_keys_list_separate_graphs)      - [ [keys], [keys], ...] - several graphs ...

              (labels_for_separate_graphs)          - list of labels for separate graphs

              (flat_keys_index)                     - add all flat keys starting from this index 
              (flat_keys_index_end)                 - add all flat keys ending with this index (default #min)

              (out_to_file)                         - save picture to file, if supported

              Graphical parameters:
                plot_type                  - mpl_2d_scatter
                point_style                - dict, setting point style for each separate graph {"0", "1", etc}

                x_ticks_period             - (int) for bar graphs, put periodicity when to show number 


            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    o=i.get('out','')

    pst=i.get('point_style',{})

    otf=i.get('out_to_file','')

    xtp=i.get('x_ticks_period','')
    if xtp=='' or xtp==0: xtp=1
    if xtp!='': xtp=int(xtp)

    lsg=i.get('labels_for_separate_graphs',[])

    # Check if table already there
    table=i.get('table',[])
    if len(table)==0:
       # Get table from entries
       tmp_a=i.get('action','')
       tmp_mu=i.get('module_uoa','')

       i['action']='get'
       i['module_uoa']=cfg['module_deps']['experiment']

       r=ck.access(i)
       if r['return']>0: return r

       table=r['table']

       rk=r['real_keys']

       i['action']=tmp_a
       i['module_uoa']=tmp_mu
    else:
       # If sort/substitute

       si=i.get('sort_index','')
       if si!='':
          rx=ck.access({'action':'sort_table', 
                        'module_uoa':cfg['module_deps']['experiment'], 
                        'table':table, 
                        'sort_index':si})
          if rx['return']>0: return rx
          table=rx['table']

       # Substitute all X with a loop (usually to sort Y and compare with predictions in scatter graphs, etc)
       if i.get('substitute_x_with_loop','')=='yes':
          rx=ck.access({'action':'substitute_x_with_loop', 
                        'module_uoa':cfg['module_deps']['experiment'], 
                        'table':table})
          if rx['return']>0: return rx
          table=rx['table']

    if len(table)==0:
       return {'return':1, 'error':'no points found'}

    # Prepare libraries
    pt=i.get('plot_type','')
    if pt.startswith('mpl_'):

   #    import numpy as np
       import matplotlib as mpl

       if ck.cfg.get('use_internal_engine_for_plotting','')=='yes':
          mpl.use('Agg') # if XWindows is not installed, use internal engine

       import matplotlib.pyplot as plt

       # Set font
       font=i.get('font',{})
       if len(font)==0:
          font = {'family':'arial', 
                  'weight':'normal', 
                  'size': 10}

       plt.rc('font', **font)

       # Configure graph
       gs=cfg['mpl_point_styles']

       sizex=i.get('mpl_image_size_x','')
       if sizex=='': sizex='9'

       sizey=i.get('mpl_image_size_y','')
       if sizey=='': sizey='5'

       dpi=i.get('mpl_image_dpi','')
       if dpi=='': dpi='100'

       if sizex!='' and sizey!='' and dpi!='':
          fig=plt.figure(figsize=(int(sizex),int(sizey)))
       else:
          fig=plt.figure()

       if i.get('plot_grid','')=='yes':
          plt.grid(True)

       bl=i.get('bound_lines','')

       sp=fig.add_subplot(111)
   #    sp.set_yscale('log')

       # Find min/max in all data and all dimensions
       tmin=[]
       tmax=[]

       for g in table:
           gt=table[g]
           for k in gt:
               for d in range(0, len(k)):
                   v=k[d]
                   if len(tmin)<=d:
                      tmin.append(v)
                      tmax.append(v)
                   else:
                      if v<tmin[d]: tmin[d]=v
                      if v>tmax[d]: tmax[d]=v 
                              
       # If density, find min and max for both graphs:
       if pt=='mpl_1d_density' or pt=='mpl_1d_histogram':
          dmean=0.0
          start=True
          dmin=0.0
          dmax=0.0
          it=0
          dt=0
          for g in table:
              gt=table[g]

              for k in gt:
                  v=k[0]

                  if v!=None:
                     if start: 
                        dmin=v
                        start=False
                     else: 
                        dmin=min(dmin, v)

                     if start: 
                        dmax=v
                        start=False
                     else: 
                        dmax=max(dmax, v)

                     it+=1
                     dt+=v

          if it!=0: dmean=dt/it

       xmin=i.get('xmin','')
       xmax=i.get('xmax','')
       ymin=i.get('ymin','')
       ymax=i.get('ymax','')

       if xmin!='':
          sp.set_xlim(left=float(xmin))
       if xmax!='':
          sp.set_xlim(right=float(xmax))
       if ymin!='':
          sp.set_ylim(bottom=float(ymin))
       if ymax!='':
          sp.set_ylim(top=float(ymax))

       xerr=i.get('display_x_error_bar','')
       yerr=i.get('display_y_error_bar','')

       if pt=='mpl_2d_bars' or pt=='mpl_2d_lines':
          ind=[]
          gt=table['0']
          xt=0
          for q in gt:

              xt+=1

              if xt==xtp: 
                 v=q[0]
                 xt=0
              else: 
                 v=0

              ind.append(v)

          sp.set_xticks(ind)
          sp.set_xticklabels(ind, rotation=-20)

          width=0.9/len(table)

       # Iterate over separate graphs and add points
       s=0

       for g in sorted(table, key=int):
           gt=table[g]

           lbl=''
           if s<len(lsg): lbl=lsg[s]

           xpst=pst.get(g,{})

           elw=int(xpst.get('elinewidth',0))

           cl=xpst.get('color','')
           if cl=='': cl=gs[s]['color']

           sz=xpst.get('size','')
           if sz=='': sz=gs[s]['size']

           mrk=xpst.get('marker','')
           if mrk=='': mrk=gs[s]['marker']

           lst=xpst.get('line_style','')
           if lst=='': lst=gs[s].get('line_style', '-')

           if pt=='mpl_2d_scatter' or pt=='mpl_2d_bars' or pt=='mpl_2d_lines':
              mx=[]
              mxerr=[]
              my=[]
              myerr=[]

              for u in gt:
                  iu=0

                  # Check if no None
                  partial=False
                  for q in u:
                      if q==None:
                         partial=True
                         break

                  if not partial:
                     mx.append(u[iu])
                     iu+=1

                     if xerr=='yes':
                        mxerr.append(u[iu])
                        iu+=1 

                     my.append(u[iu])
                     iu+=1

                     if yerr=='yes':
                        myerr.append(u[iu])
                        iu+=1 

              if pt=='mpl_2d_bars':
                 mx1=[]
                 for q in mx:
                     mx1.append(q+width*s)

                 if yerr=='yes':
                    sp.bar(mx1, my, width=width, edgecolor=cl, facecolor=cl, align='center', yerr=myerr, label=lbl) # , error_kw=dict(lw=2))
                 else:
                    sp.bar(mx1, my, width=width, edgecolor=cl, facecolor=cl, align='center', label=lbl)

              elif pt=='mpl_2d_lines':

                 if yerr=='yes':
                     sp.errorbar(mx, my, yerr=myerr, ls='none', c=cl, elinewidth=elw)
                 sp.plot(mx, my, c=cl, label=lbl)


              else:
                 if xerr=='yes' and yerr=='yes':
                    sp.errorbar(mx, my, xerr=mxerr, yerr=myerr, ls='none', c=cl, elinewidth=elw, label=lbl)
                 elif xerr=='yes' and yerr!='yes':
                    sp.errorbar(mx, my, xerr=mxerr, ls='none',  c=cl, elinewidth=elw, label=lbl)
                 elif yerr=='yes' and xerr!='yes':
                     sp.errorbar(mx, my, yerr=myerr, ls='none', c=cl, elinewidth=elw, label=lbl)
                 else:
                    sp.scatter(mx, my, s=int(sz), edgecolor=cl, c=cl, marker=mrk, label=lbl)

                 if xpst.get('frontier','')=='yes':
                    # not optimal solution, but should work (need to sort to draw proper frontier)
                    a=[]
                    for q in range(0, len(mx)):
                        a.append([mx[q],my[q]])

                    b=sorted(a, key=lambda k: k[0])

                    mx=[tmin[0]]
                    my=[tmax[1]]

                    for j in b:
                        mx.append(j[0])
                        my.append(j[1])

                    mx.append(tmax[0])
                    my.append(tmin[1])

                    sp.plot(mx, my, c=cl, linestyle=lst, label=lbl)

           elif pt=='mpl_1d_density' or pt=='mpl_1d_histogram':
              if not start: # I.e. we got non empty points
                 xbins=i.get('bins', 100)

                 mx=[]
                 for u in gt:
                     mx.append(u[0])

                 ii={'action':'analyze',
                     'min':dmin,
                     'max':dmax,
                     'module_uoa':cfg['module_deps']['math.variation'],
                     'bins':xbins,
                     'characteristics_table':mx}

                 r=ck.access(ii)
                 if r['return']>0: return r

                 xs=r['xlist']
                 dxs=r['ylist']

                 pxs=r['xlist2s']
                 dpxs=r['ylist2s']

                 if pt=='mpl_1d_density':
                    sp.plot(xs,dxs, label=lbl)
                    sp.plot(pxs, dpxs, 'x', mec='r', mew=2, ms=8) #, mfc=None, mec='r', mew=2, ms=8)
                    sp.plot([dmean,dmean],[0,dpxs[0]],'g--',lw=2)
                 else:
                    plt.hist(mx, bins=xbins, normed=True, label=lbl)

           s+=1
           if s>=len(gs):s=0

       if bl=='yes':
          xbs=i.get('bound_style',':')
          xbc=i.get('bound_color','r')
          sp.plot([tmin[0],tmax[0]],[tmin[1],tmin[1]], linestyle=xbs, c=xbc)
          sp.plot([tmin[0],tmin[0]],[tmin[1],tmax[1]], linestyle=xbs, c=xbc)

       # Set axes names
       axd=i.get('axis_x_desc','')
       if axd!='': plt.xlabel(axd)

       ayd=i.get('axis_y_desc','')
       if ayd!='': plt.ylabel(ayd)

       atitle=i.get('title','')
       if atitle!='': plt.title(atitle)

#       handles, labels = plt.get_legend_handles_labels()
       plt.legend()#handles, labels)

       if otf=='':
          plt.show()
       else:
          plt.savefig(otf)

    else:
       return {'return':1, 'error':'this type of plot ('+pt+') is not supported'}

    return {'return':0}

##############################################################################
# Continuously updated plot

def continuous_plot(i):
    """
    Input:  {

            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    for q in range(0, 1000):
        r=plot(i)
        if r['return']>0: return r

        x=ck.inp({'text':'Press any key'})

    return {'return':0}
