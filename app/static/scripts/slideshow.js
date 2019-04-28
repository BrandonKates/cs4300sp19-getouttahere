var slide_num = Math.floor(Math.random()*13);
				
				function load_image(source, id){
					var img = document.createElement("img");
					img.src = source;
					img.id = id;
					img.alt = "Slide";
					img.classList.add("image");
					img.classList.add("img-responsive");
					img.classList.add("slide");
					document.getElementById("slideshow").appendChild(img);
					setTimeout(function(){
					img.classList.add("in");
					},0);

				}
				var sources = [];
				for(i=1; i<= 13; i++){
					sources.push("/static/images/img" + i + ".jpg");
				}
				var prev_id;
				function slideshow(){
					var to_unload = slide_num - 2;
					if(to_unload <= 0){
						to_unload = 11 + slide_num;
					}
					
					var i;
					var id;
					for (i = 0; i < sources.length; i++) {
						id = "img" + String(i+1);
						if(i == slide_num){
							load_image(sources[i], id);
							break;
						}
					}
					curr_img = document.getElementById(id);
					
					//weird workaround for fade out not working
					if(document.getElementById(prev_id) != null){
						prev_img = document.getElementById(prev_id);
						prev_img.style.opacity = 0;
					}
					prev_id = id;
					if(document.getElementById("img" + String(to_unload)) != null){ //unload image from 2 images ago
						document.getElementById("img" + String(to_unload)).remove()
					}
					slide_num++;

					if (slide_num >= sources.length) {slide_num = 0;} 
					setTimeout(slideshow, 7000); // Change image every 7 seconds
	
				}
				slideshow();