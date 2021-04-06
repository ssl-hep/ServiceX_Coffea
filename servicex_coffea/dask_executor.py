# Copyright (c) 2019, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from typing import Optional
from dask.distributed import Client
from .executor import run_coffea_processor, Executor


class DaskExecutor(Executor):
    def __init__(self, client_addr: Optional[str] = None):
        '''Create a Dask executor to process the analysis

        Args:
            client_addr (Optional[str]): If `None` then create a local cluster that runs in-process.
                                         Otherwise connect to an already existing cluster.
        '''
        self.is_local = client_addr is None
        self.dask = Client(threads_per_worker=10, asynchronous=True) if self.is_local \
            else Client(client_addr, asynchronous=True)

    def get_result_file_stream(self, datasource):
        if self.is_local:
            return datasource.stream_result_files()
        else:
            return datasource.stream_result_file_urls()

    def run_async_analysis(self, file_url, tree_name, accumulator, process_func):
        data_result = self.dask.submit(run_coffea_processor,
                                       events_url=file_url,
                                       tree_name=tree_name,
                                       accumulator=accumulator,
                                       proc=process_func)
        print("Data Result ", data_result)

        return data_result