#version 120

varying vec2 fTexcoords;
uniform sampler2D textureObj;
uniform vec3 iResolution;
uniform float iTime;

#define param 0.63

void main()
{
    vec2 p = (2.0 * fTexcoords - iResolution.xy) / iResolution.y;
    p *= 4.0;
	p = mod(p,4.0)-2.0;
    //p = abs(p);


    for(int i=0; i<4; i++)
    {
        // the magic formula by Kali.
    	p = abs(p)/dot(p,p)-param;
        //p = pow(abs(p), vec2(sin(iTime*0.5)*0.2+1.1))/dot(p,p)-param;
    	p *= 2.0;
    };
    p /= 2.0;

    float de = abs(dot(p,vec2(cos(iTime), sin(iTime))));
 	gl_FragColor = vec4(vec3(de),1.0);
    gl_FragColor = texture2D(textureObj, fTexcoords);
}