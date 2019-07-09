#include<iostream>

class Pod {
    private:
        int x, y, dir, health;
        float vx, vy;

    public:
        Pod(){}

        int getX() { return x;}
        int getY() { return y;}
        int getDir() { return dir;}
        int getHealth() { return health;}
        float getVx() { return vx;}
        float getVy() { return vy;}
        void setX(int x) { this->x = x;}
        void setY(int y) { this->y = y;}
        void setDir(int dir) { this->dir = dir;}
        void setHealth(int health) { this->health = health;}
        void setVx(float vx) { this->vx = vx;}
        void setVy(float vy) { this->vy = vy;}

        friend std::ostream& operator<<(std::ostream& os, const Pod p) {
            os << "Pod=[";
            os << "x=" << p.x << ", "; 
            os << "y=" << p.y << ", ";
            os << "vx=" << p.vx << ", ";
            os << "vy=" << p.vy << ", ";
            os << "dir=" << p.dir << ", ";
            os << "health=" << p.health << "]";
            return os;
        }

};