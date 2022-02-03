filetype plugin indent on
set tabstop=4
set shiftwidth=4
set expandtab

autocmd BufWritePre * :%s/\s\+$//e

set number

let @l='i_logger.warning(f"{OF=}")'
