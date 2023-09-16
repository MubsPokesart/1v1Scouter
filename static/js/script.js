function formatTeam (arr){
    /*const teamStorage = document.getElementById('team_data')
    const newbr = document.createElement('br')*/
    
    let outer = '', inner_content = ''
    for (let i = 0; i < arr.length; i++){
        if ((typeof(arr[i]) == 'object')){
            if (arr[i].length > 0) 
                inner_content = inner_content + `(${arr[i].join(' / ')})`
        } else if (arr[i].match(/https:\/\//) ) {
            outer = arr[i]
        } else if (arr[i].length == 1){
            inner_content = inner_content + ` (${arr[i]})`
        } else {
            arr[i] = arr[i].replace(' ', '-')
            switch (arr[i]){
                case 'Urshifu-*':
                    arr[i] = 'Urshifu'
                    break
                case 'Type:-Null':
                    arr[i] = 'type-null'
                    break
            }
            inner_content = inner_content + `<img src="https://www.smogon.com/forums//media/minisprites/${arr[i].toLowerCase()}.png">`
        } 
    }
    
    /*newbr.innerHTML= (`<a href="${outer}" target=”blank” rel="noopener noreferrer">${inner_content}</a>`)
    teamStorage.append(newbr)*/

    return `<a href="${outer}" target=”blank” rel="noopener noreferrer" style="text-decoration: none; color: #000000; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">${inner_content}</a>`
}

