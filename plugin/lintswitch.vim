" lintswitch.vim
" Graham King (http://gkgk.org)
"
" Copy this file into ./vim/plugin/
" Make sure the lintswitch server is running.

if !has('python')
"     echo 'Error: lintswitch.vim requires Vim to be compiled with +python'
    finish
endif

function! LintSwitch()
    python << END
import vim
import socket
try:
    s = socket.create_connection(('127.0.0.1', 4008), 2)
    s.send('%s\n' % vim.current.buffer.name)
    s.close()
except socket.error:
    pass
END
endfunction

autocmd! BufWritePost,FileWritePost * :call LintSwitch()
