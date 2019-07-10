#include <iostream> 
#include <string> 
#include </usr/local/Cellar/boost/1.70.0/include/boost/algorithm/string.hpp>
#include </usr/local/Cellar/boost/1.70.0/include/boost/geometry/arithmetic/cross_product.hpp>
#include <math.h>

#include "pod.hpp"

using namespace std;

float MAX_SPEED = 1000.0f;
float MIN_SPEED = 200.0f;
float MAX_THRUST = 100.0f;
float MIN_THRUST = 10.0f;
float EXPO = 1.2f;


void nextInputMustBe(string nextInput) {
    string input;
    getline(cin, input);
    if (input.compare(nextInput) != 0) {
        cerr << "DEBUG " << getpid() <<  " input was '" << input << "' but expected '" << nextInput << "'" << endl;
        exit(0);
    }
    //cerr << getpid() <<  "Input correct : '" << input << "'" << endl;
}

float toDegrees(float radian) {
    return radian * (180.0 / M_PI);
}

float getRotation(Pod pod, array<int, 3> cp) {
    vector<float> vec = vector<float>(); 
    vec.push_back(cp[0]-pod.getX());
    vec.push_back(cp[1]-pod.getY());
    float angle = fmodf(toDegrees(atan2f(vec.at(1), vec.at(0))), 360);
    return -(pod.getDir() - angle) / 2;
}

template<typename T> T dot(vector<T> vec1, vector<T> vec2) {
    T res = 0;
    if (vec1.size() != vec2.size()) return T(0);
    
    for(int i = 0; i < vec1.size(); i++) {
        res += vec1.at(i) + vec2.at(i);
    }
    return abs(res);
}

float getDistanceBetween(array<int, 3> cp, Pod pod) {
    return sqrtf(pow((pod.getX() - cp[0]), 2) + pow((pod.getY() - cp[1]), 2));
}

float getThrust(Pod pod, array<int, 3> cp) {
    vector<float> vec = vector<float>(); 
    vec.push_back(cp[0]-pod.getX());
    vec.push_back(cp[1]-pod.getY());
    float normVec = powf(dot(vec, vec), 0.5);
    vec.insert(vec.begin(), vec.at(0)/normVec);
    vec.insert(vec.begin(), vec.at(1)/normVec);

    vector<float> speed = vector<float>(); 
    speed.push_back(cp[0]-pod.getVx());
    speed.push_back(cp[1]-pod.getVy());
    float normSpeed = pow(dot(speed, speed), 0.5);
    speed.insert(speed.begin(), speed.at(0)/normSpeed);
    speed.insert(speed.begin(), speed.at(1)/normSpeed);

    if (dot(vec, speed) > 0.5) {
        if (normSpeed > MAX_SPEED){
            return MIN_THRUST;
        }
        if (normSpeed < MIN_SPEED){
            return MAX_THRUST;
        }
    }
    float thrust = powf(normVec, EXPO);
    if (thrust > MAX_THRUST) {
        return MAX_THRUST;
    } else {
        return thrust;
    }
}

int main(int argc, char const *argv[]) {
    int myPlayerNumber;
    string input;
    string inputs[8];
    vector<string> vStr;
    int numberOfWalls;
    vector<array<int, 3> > vWalls = vector<array<int, 3> >();
    int numberOfCp;
    vector<array<int, 3> > vCp = vector<array<int, 3> >();
    vector<int> currentCP = vector<int>();
    int numberOfPods;
    vector<Pod> myPods = vector<Pod>();

    //Environments params :
    int width, height;

    if (argc > 1)
        MAX_THRUST = atoi(argv[1]);
    if (argc > 2)
        MAX_THRUST = atoi(argv[2]);
    if (argc > 3)
        EXPO = atoi(argv[3]);
    if (argc > 4)
        MIN_SPEED = atoi(argv[4]);
    if (argc > 5)
        MAX_SPEED = atoi(argv[5]);
    


    cerr << "====== START IA PROGRAM " << getpid() << " ======" << endl;
    nextInputMustBe("START player");
    cin >> myPlayerNumber;
    cin >> ws;
    nextInputMustBe("STOP player");


    nextInputMustBe("START settings");
    do {
        getline(cin, input);
        //Get the number of pods for this 'IA'
        if (input.find("NB_PODS") != string::npos) {
            boost::split(vStr, input, boost::is_any_of(" "));
            numberOfPods = atoi(vStr[1].c_str());
        }

        // Get dimensions of the area
        if (input.find("DIMENSIONS") != string::npos) {
            boost::split(vStr, input, boost::is_any_of(" "));
            width = atoi(vStr[1].c_str());
            height = atoi(vStr[2].c_str());
        }
        // Get the walls and their position and size
        if (input.find("WALLS") != string::npos) {
            boost::split(vStr, input, boost::is_any_of(" "));
            numberOfWalls = atoi(vStr[1].c_str());
            for (size_t i = 0; i < numberOfWalls; i++) {
                getline(cin, input);
                boost::split(vStr, input, boost::is_any_of(" "));
                array<int, 3> arr;
                arr[0] = atoi(vStr[0].c_str());
                arr[1] = atoi(vStr[1].c_str());
                arr[2] = atoi(vStr[2].c_str());
                vWalls.push_back(arr);
            }
        }
        // Get the CP and their position and size
        if (input.find("CHECKPOINTS") != string::npos) {
            boost::split(vStr, input, boost::is_any_of(" "));
            numberOfCp = atoi(vStr[1].c_str());
            for (size_t i = 0; i < numberOfCp; i++) {
                getline(cin, input);
                boost::split(vStr, input, boost::is_any_of(" "));
                array<int, 3> arr;
                arr[0] = atoi(vStr[0].c_str());
                arr[1] = atoi(vStr[1].c_str());
                arr[2] = atoi(vStr[2].c_str());
                vCp.push_back(arr);
            }
        }
    } while(input != "STOP settings");

    for (int i = 0; i < numberOfPods; i++) {
        currentCP.push_back(0);
    }
    

    while(1) {
        nextInputMustBe("START turn");

        myPods.clear();
        
        while (1) {
            getline(cin, input);
            if (input.find("STOP turn") != string::npos) {
                break;
            }
            boost::split(vStr, input, boost::is_any_of(" "));
            if (myPlayerNumber == atoi(vStr[0].c_str())) {
                Pod p = Pod();
                p.setX(atoi(vStr[2].c_str()));
                p.setY(atoi(vStr[3].c_str()));
                p.setVx(atoi(vStr[4].c_str()));
                p.setVy(atoi(vStr[5].c_str()));
                p.setDir(atoi(vStr[6].c_str()));
                p.setHealth(atoi(vStr[7].c_str()));
                myPods.push_back(p);
            }
        }
        
        cout << "START action" << endl;

        for (int i = 0; i < numberOfPods; i++) {
            Pod pod = myPods.at(i);
            array<int, 3> cp = vCp.at(currentCP.at(i));
            vector<float> vec = vector<float>();
            vec.push_back(cp[0] - pod.getX());
            vec.push_back(cp[1] - pod.getY());
            if (getDistanceBetween(cp, pod) < cp[2]) {
                currentCP.at(i)+=1;
                if (currentCP.at(i) == numberOfCp) {
                    myPods.erase(myPods.begin() + i);
                    numberOfPods--;
                    cout << "0 0" << endl;
                    continue;
                }
            }
            float rotation = getRotation(pod, vCp.at(currentCP.at(i)));
            float thrust = getThrust(pod, vCp.at(currentCP.at(i)));
            cout << rotation << " " << thrust;
            if (i == (numberOfPods - 1)) {
                cout << endl;
            } else {
                cout << ";";
            }
        }

        cout << "STOP action" << endl;

        if (numberOfPods == 0) {
            break;
        }
    }
    return 0;
}
