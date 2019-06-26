# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import ntpath
from PIL import Image
import subprocess

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.DataFileUtilClient import DataFileUtil as DFUClient

#END_HEADER


class CGView:
    '''
    Module Name:
    CGView

    Module Description:
    A KBase module: CGView
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kellyhuang21/CircularGenome.git"
    GIT_COMMIT_HASH = "24002a39f02d947880d40e20d14889b44293820c"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        # logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
        #                     level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_CGView(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_CGView
        print('Starting run_kellyhuangCGView function. Params=')
        print(params)
        # Validating workspace_name and input_file is present
        print('Validating parameters.')
        if 'workspace_name' not in params:
            raise ValueError('Parameter workspace_name is not set in input arguments')
        workspace_name = params['workspace_name']
        if 'input_file' not in params:
            raise ValueError('Parameter input_file is not set in input arguments')

        input_file = params['input_file']

        # Set up CCT project_folder
        subprocess.call("cd /opt/cgview_comparison_tool && ./update_cogs.sh && cgview_comparison_tool.pl -p project", shell=True)

        # Turn genome object to Genbank file
        gfu = GenomeFileUtil(self.callback_url)
        gbk = gfu.genome_to_genbank({'genome_ref':input_file})
        gbk_file = gbk["genbank_file"]["file_path"]
        subprocess.call(["cp", gbk_file, "/opt/cgview_comparison_tool/project/reference_genome"])
        base = ntpath.basename(gbk_file).rsplit(".", 1)[0]
        name_gbff =  base + ".gbff"
        name_gbk = base + ".gbk"
        from_path = "/opt/cgview_comparison_tool/project/reference_genome/" + name_gbff
        print("===== from", from_path)
        to_path = "/opt/cgview_comparison_tool/project/reference_genome/" + name_gbk
        print("===== to", to_path)
        subprocess.call(["mv", from_path, to_path])

        # Add Genbank file to project_folder/reference_genome
        # Generate map from Genbank file
        # subprocess.call("cgview_comparison_tool.pl -p project", shell=True)
        os.chdir("/opt/cgview_comparison_tool")
        proc = subprocess.Popen(["cgview_comparison_tool.pl", "-p", "/opt/cgview_comparison_tool/project"], stdout=subprocess.PIPE)
        # for line in proc.stdout:
        #     print(line)
        proc.wait()
        subprocess.call(["cgview_comparison_tool.pl",  "-p", " project"], shell=True)

        # Retrieve map PNG from project_folder/maps
        output_dir= os.path.join(self.shared_folder, 'output_folder')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        subprocess.call(["cp", "/opt/cgview_comparison_tool/project/maps/medium.png", output_dir])
        # subprocess.call(["cp", "/opt/cgview_comparison_tool/project/maps/medium.html", output_dir])

        output_png_file_path = os.path.join(output_dir, 'medium.png')
        html_file = os.path.join(output_dir, 'index.html')
        with open(html_file, 'w') as html_handle:
            html_handle.write(f'<img src="{output_dir + "/" + "medium.png"}" width="100%" height="100%"></img>')
        html_handle.close()

        dfu = DFUClient(self.callback_url)
        try:
            png_upload_ret = dfu.file_to_shock({'file_path': output_png_file_path, 'make_handle': 0})
        except:
            raise ValueError('Logging exception loading png_file to shock')
        try:
            upload_ret = dfu.file_to_shock({'file_path': output_dir,
                                            'make_handle': 0,
                                            'pack': 'zip'})
        except:
            raise ValueError('Logging exception loading html_report to shock')
        reportObj = {'direct_html_link_index': 0,
                     # 'file_links': [],
                     'html_links': [],
                     'workspace_name': params['workspace_name']
                     }
        # reportObj['file_links'] = [{'shock_id': png_upload_ret['shock_id'],
        #                             'name': 'medium.png',
        #                             'label': 'PNG'}]
        reportObj['html_links'] = [{'path':output_dir,
                                    # 'shock_id': upload_ret['shock_id'],
                                    'name': 'index.html',
                                    'label': 'html report'}
                                   ]
        reportClient = KBaseReport(self.callback_url, token=ctx['token'])
        report_info = reportClient.create_extended_report(reportObj)

        # # Resize image
        # basewidth = 300
        # img = Image.open('/opt/cgview_comparison_tool/project/maps/medium.png')
        # wpercent = (basewidth/float(img.size[0]))
        # hsize = int((float(img.size[1])*float(wpercent)))
        # img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        # # img = img.resize((600, 600), Image.ANTIALIAS)
        # img.save('/opt/cgview_comparison_tool/project/maps/medium1.png', "PNG", optimize=True)
        # # # print("=====", os.listdir("/opt/cgview_comparison_tool/project/maps/"))
        # # subprocess.call(["cp", "/opt/cgview_comparison_tool/project/maps/medium1.png", self.shared_folder])
        # png_dir = os.path.join(self.shared_folder, 'medium1.png')
        # html_file = os.path.join(output_dir, 'index.html')
        # with open(html_file, 'w') as html_handle:
        #     html_handle.write(f'<img src="{output_dir + "/" + "medium.png"}" width="100%" height="100%"></img>')
        # html_handle.close()
        # print("=======output_folder", os.listdir(output_dir))
        #
        # report_client = KBaseReport(self.callback_url)
        # dfu = DFUClient(self.callback_url)
        # try:
        # #upload_ret = dfu.file_to_shock({'file_path': html_file,
        #     upload_ret = dfu.file_to_shock({'file_path': output_dir,
        #                                     'make_handle': 0,
        #                                     'pack': 'zip'})
        # except:
        #     raise ValueError('Logging exception loading html_report to shock')
        # try:
        #     png_upload_ret = dfu.file_to_shock({'file_path': os.path.join(output_dir, "medium.png"),
        #                                     'make_handle': 0})
        #     #'pack': 'zip'})
        # except:
        #     raise ValueError('Logging exception loading png_file to shock')
        #
        #
        # png_dict = {'shock_id': png_upload_ret['shock_id'], 'path':png_dir, 'name': 'Circular_Genome_Map_PNG'}
        # html_dict = {'shock_id': upload_ret['shock_id'], 'path': output_dir,'name':'index.html'}
        # report = report_client.create_extended_report({
        #     'direct_html_link_index': 0,
        #     'html_links':[html_dict],
        #     'file_links':[png_dict],
        #     'workspace_name': params['workspace_name'],
        # })

        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_CGView

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_CGView return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
