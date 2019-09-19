#include <algorithm>

#include "Piece.hpp"

using namespace std;



void Piece::SetShape(PieceShape shape)
{
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 2; j++)
            coords[i][j] = pieceCoords[shape][i][j];
    pieceShape = shape;
}

void Piece::SetRandomShape()
{
    int rand_shape_idx =  7; // rand() % 7 + 1;
    SetShape(PieceShape(rand_shape_idx));
}



void Piece::SetPlayerShape()
{
    int rand_shape_idx =  3; // rand() % 7 + 1;
    SetShape(PieceShape(rand_shape_idx));
}

